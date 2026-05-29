import logging
import os
import uuid
import boto3
from botocore.client import Config
from celery_app import celery_app
from ..worker.ocr.pipeline import pipeline
from ..db.session import SessionLocal
from ..db.models import ExtractionJob, Voter, JobStatus
from ..core.templates import engine as template_engine
from ..core.search import index_voter, bulk_index_voters
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)

# MinIO Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)

CONFIDENCE_THRESHOLD = 0.8

@celery_app.task(name="process_document")
def process_document(job_id: str, file_name: str, bucket_name: str, candidate_id: int):
    db = SessionLocal()
    
    # 1. Fetch existing Job record
    job = db.query(ExtractionJob).filter(ExtractionJob.id == job_id).first()
    if not job:
        # Fallback if job was not created by API (unlikely)
        job = ExtractionJob(id=job_id, file_name=file_name, candidate_id=candidate_id, status=JobStatus.PROCESSING)
        db.add(job)
    else:
        job.status = JobStatus.PROCESSING
    
    db.commit()
    
    local_pdf_path = f"/tmp/{file_name}"
    
    try:
        logger.info(f"Downloading {file_name} from bucket {bucket_name} to {local_pdf_path}")
        s3.download_file(bucket_name, file_name, local_pdf_path)
        
        # 2. Convert PDF to Image (OCR engines prefer images)
        logger.info(f"Converting PDF {file_name} to images (page-by-page to save memory)...")
        
        from pdf2image import pdf_info
        info = pdf_info(local_pdf_path)
        total_pages = info["Pages"]
        
        all_ocr_results = []
        pages_processed = 0
        
        # Start from page 2 to skip the cover page if multiple pages
        start_page = 2 if total_pages > 1 else 1
        
        for page_num in range(start_page, total_pages + 1):
            logger.info(f"Processing page {page_num}/{total_pages}...")
            # Convert single page to image
            images = convert_from_path(local_pdf_path, first_page=page_num, last_page=page_num)
            if not images:
                logger.warning(f"Failed to convert page {page_num}")
                continue
                
            image = images[0]
            temp_image_path = f"/tmp/{job_id}_page{page_num}.jpg"
            image.save(temp_image_path, "JPEG")
            
            # 3. Run OCR Pipeline
            page_results = pipeline.process(temp_image_path)
            
            # Tag results with page number
            for res in page_results:
                res.page_num = page_num
            
            all_ocr_results.extend(page_results)
            pages_processed += 1
            
            # Clean up temp image
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
        
        if os.path.exists(local_pdf_path):
            os.remove(local_pdf_path)
            
        if pages_processed == 0:
            raise Exception("Failed to extract any pages from PDF")
        
        # 5. Apply Template
        template = template_engine.get_template("maharashtra_voter_roll")
        if not template:
            raise Exception("Required template 'maharashtra_voter_roll' not found")
        
        from ..core.extractor import extract_fields
        voters_data = extract_fields(all_ocr_results, template)
        logger.info(f"Extracted {len(voters_data)} voter records from {pages_processed} pages")
        
        avg_confidence = sum(r.confidence for r in all_ocr_results) / len(all_ocr_results) if all_ocr_results else 0
        
        voters_to_index = []
        for voter_data in voters_data:
            # Ensure we have at least some identifiers
            if not voter_data.get("voter_id"):
                voter_data["voter_id"] = "NOT_FOUND"
            if not voter_data.get("full_name"):
                voter_data["full_name"] = "COULD NOT EXTRACT"
            if not voter_data.get("age"):
                voter_data["age"] = "0"
            if not voter_data.get("gender"):
                voter_data["gender"] = "Unknown"
            
            # Pop raw_ocr_data so it doesn't pollute structured_data
            record_raw_ocr = voter_data.pop("_raw_ocr_data", [])
            
            logger.info(f"Final voter data to save: {voter_data}")
            
            # 4. Save Voter records
            voter = Voter(
                job_id=job_id,
                candidate_id=candidate_id,
                voter_id=voter_data.get("voter_id", "UNKNOWN"),
                full_name=voter_data.get("full_name", "UNKNOWN"),
                structured_data=voter_data,
                raw_ocr_data=record_raw_ocr,
                confidence=avg_confidence
            )
            db.add(voter)
            voters_to_index.append(voter)
            
        # 5. Update Job Status
        if avg_confidence < CONFIDENCE_THRESHOLD:
            job.status = JobStatus.PENDING_REVIEW
        else:
            job.status = JobStatus.COMPLETED
            
        job.confidence_score = avg_confidence
        db.commit()
        
        # 6. Index to Elasticsearch if COMPLETED
        if job.status == JobStatus.COMPLETED:
            voters_to_bulk_index = []
            for v in voters_to_index:
                # Skip indexing if voter_id is NOT_FOUND to keep search index clean
                if v.voter_id and v.voter_id != "NOT_FOUND":
                    voters_to_bulk_index.append({
                        "id": v.id,
                        "voter_id": v.voter_id,
                        "candidate_id": candidate_id,
                        "full_name": v.full_name,
                        "job_id": job.id,
                        "confidence": v.confidence,
                        "structured_data": v.structured_data
                    })
            
            if voters_to_bulk_index:
                try:
                    bulk_index_voters(voters_to_bulk_index)
                    logger.info(f"Bulk indexed {len(voters_to_bulk_index)} voters for job {job_id}")
                except Exception as e:
                    logger.error(f"Failed to bulk index voters for job {job_id}: {str(e)}")
        
        logger.info(f"Job {job_id} processed. Status: {job.status}")
        return {"status": "success", "job_id": job_id, "confidence": avg_confidence}

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        db.rollback()  # Ensure session is usable after failure
        
        # Reload job in new session state if needed
        job = db.query(ExtractionJob).filter(ExtractionJob.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
