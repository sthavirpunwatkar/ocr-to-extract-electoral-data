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
from ..core.search import index_voter
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
def process_document(file_name: str, bucket_name: str):
    job_id = str(uuid.uuid4())
    db = SessionLocal()
    
    # 1. Create Job record
    job = ExtractionJob(id=job_id, file_name=file_name, status=JobStatus.PROCESSING)
    db.add(job)
    db.commit()
    
    local_pdf_path = f"/tmp/{file_name}"
    
    try:
        logger.info(f"Downloading {file_name} from bucket {bucket_name} to {local_pdf_path}")
        s3.download_file(bucket_name, file_name, local_pdf_path)
        
        # 2. Convert PDF to Image (OCR engines prefer images)
        logger.info(f"Converting PDF {file_name} to images...")
        images = convert_from_path(local_pdf_path, first_page=1, last_page=1) # Process first page for now
        
        if not images:
            raise Exception("Failed to convert PDF to images")
            
        temp_image_path = f"/tmp/{job_id}_page1.jpg"
        images[0].save(temp_image_path, "JPEG")
        
        logger.info(f"Processing document image: {temp_image_path} (Job: {job_id})")
        
        # 3. Run OCR Pipeline
        ocr_results = pipeline.process(temp_image_path)
        
        # 4. Clean up temp image
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        if os.path.exists(local_pdf_path):
            os.remove(local_pdf_path)
        
        # 5. Apply Template
        template = template_engine.get_template("maharashtra_voter_roll")
        
        from ..core.extractor import extract_fields
        voters_data = extract_fields(ocr_results, template)
        logger.info(f"Extracted {len(voters_data)} voter records")
        
        avg_confidence = sum(r.confidence for r in ocr_results) / len(ocr_results) if ocr_results else 0
        
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
                voter_id=voter_data.get("voter_id", "UNKNOWN"),
                full_name=voter_data.get("full_name", "UNKNOWN"),
                structured_data=voter_data,
                raw_ocr_data=record_raw_ocr,
                confidence=avg_confidence
            )
            db.add(voter)
            voters_to_index.append(voter)
            
            # Index to Elasticsearch if COMPLETED
            # Wait, we do this later in the original code, but doing it here might be easier if we need the voter object.
            # Original code did it after committing. Let's just defer elasticsearch to the existing block or move it.
            
        # 5. Update Job Status
        if avg_confidence < CONFIDENCE_THRESHOLD:
            job.status = JobStatus.PENDING_REVIEW
        else:
            job.status = JobStatus.COMPLETED
            
        job.confidence_score = avg_confidence
        db.commit()
        
        # 6. Index to Elasticsearch if COMPLETED
        if job.status == JobStatus.COMPLETED:
            for v in voters_to_index:
                index_voter(
                    voter_id=v.voter_id,
                    full_name=v.full_name,
                    job_id=job.id,
                    confidence=v.confidence,
                    structured_data=v.structured_data
                )
        
        logger.info(f"Job {job_id} processed. Status: {job.status}")
        return {"status": "success", "job_id": job_id, "confidence": avg_confidence}

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        db.commit()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
