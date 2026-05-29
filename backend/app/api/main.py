import os
import uuid
import boto3
import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from botocore.client import Config
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from celery_app import celery_app
from app.core.search import search_voters, create_index
from app.db.session import get_db, engine
from app.db.models import Base, Voter, User, UserRole, Candidate, JobStatus, ExtractionJob
from app.schemas.extraction import VoterSyncUpdate, VoterResponse, CandidateCreate, CandidateResponse
from app.core.auth import (
    get_current_active_user, 
    require_role, 
    verify_password, 
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from prometheus_fastapi_instrumentator import Instrumentator

from starlette.middleware.cors import CORSMiddleware

# MinIO Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "documents")

s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)

app = FastAPI(title="OCR API")

# Candidate Management
@app.post("/candidates", response_model=CandidateResponse)
async def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    db_candidate = Candidate(**candidate.dict())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

@app.get("/candidates", response_model=List[CandidateResponse])
async def list_candidates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    return db.query(Candidate).all()

@app.post("/candidates/{candidate_id}/assets")
async def upload_candidate_assets(
    candidate_id: int,
    logo: UploadFile = File(None),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if logo:
        logo_name = f"candidate_{candidate_id}_logo_{uuid.uuid4()}{os.path.splitext(logo.filename)[1]}"
        s3.upload_fileobj(logo.file, MINIO_BUCKET_NAME, logo_name)
        candidate.logo_url = logo_name

    if profile_image:
        img_name = f"candidate_{candidate_id}_profile_{uuid.uuid4()}{os.path.splitext(profile_image.filename)[1]}"
        s3.upload_fileobj(profile_image.file, MINIO_BUCKET_NAME, img_name)
        candidate.profile_image_url = img_name

    db.commit()
    return {"message": "Assets uploaded successfully", "logo_url": candidate.logo_url, "profile_image_url": candidate.profile_image_url}

@app.get("/extraction-jobs")
async def list_jobs(
    candidate_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR]))
):
    query = db.query(ExtractionJob)
    if candidate_id:
        query = query.filter(ExtractionJob.candidate_id == candidate_id)
    return query.all()

@app.post("/extraction-jobs/{job_id}/approve")
async def approve_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR]))
):
    job = db.query(ExtractionJob).filter(ExtractionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.status = JobStatus.APPROVED
    db.commit()
    return {"message": "Job approved"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:52448",
        "http://localhost:62096",
        "http://localhost:8080",
        "http://10.0.2.2",         # Android Emulator
        "http://127.0.0.1",
        "*",                       # Allow all for development flexibility
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_charset_header(request, call_next):
    response = await call_next(request)
    content_type = response.headers.get("Content-Type")
    if content_type and "application/json" in content_type.lower() and "charset" not in content_type.lower():
        response.headers["Content-Type"] = f"{content_type}; charset=utf-8"
    return response

# Initialize Prometheus Instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.on_event("startup")
async def startup_event():
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    
    # Create initial admin user if not exists
    from app.db.session import SessionLocal
    from app.core.auth import get_password_hash
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            print("Initial admin user created: admin/admin123")
    finally:
        db.close()

    # Initialize Elasticsearch index
    try:
        create_index()
    except Exception as e:
        print(f"Failed to create Elasticsearch index: {e}")

# Ensure bucket exists
try:
    s3.head_bucket(Bucket=MINIO_BUCKET_NAME)
except:
    s3.create_bucket(Bucket=MINIO_BUCKET_NAME)

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "candidate_id": user.candidate_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def root():
    return {"message": "OCR API is running"}

@app.post("/upload")
async def upload_document(
    candidate_id: int = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.BOOTH_LEAD]))
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # File size validation (max 50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    try:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large (max 50MB)")
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        # Fallback if seek/tell fails
        pass

    file_id = str(uuid.uuid4())
    file_name = f"{file_id}_{file.filename}"
    
    try:
        # Create ExtractionJob
        job = ExtractionJob(id=file_id, candidate_id=candidate_id, file_name=file.filename, status=JobStatus.PENDING)
        db.add(job)
        db.commit()

        # Upload to MinIO
        s3.upload_fileobj(file.file, MINIO_BUCKET_NAME, file_name)
        
        # Enqueue Celery task
        celery_app.send_task("process_document", args=[file_id, file_name, MINIO_BUCKET_NAME, candidate_id])
        
        return {
            "message": "File uploaded successfully",
            "file_name": file_name,
            "job_id": file_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search(
    q: str = Query(..., min_length=1), 
    candidate_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Enforce multi-tenancy check
        if current_user.role != UserRole.ADMIN and current_user.candidate_id != candidate_id:
            raise HTTPException(status_code=403, detail="Unauthorized candidate access")

        search_result = search_voters(q, candidate_id, limit, skip)
        return {
            "results": search_result["results"],
            "total": search_result.get("total", 0),
            "transliterated": search_result["transliterated"],
            "user": current_user.username
        }
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voters", response_model=List[VoterResponse])
async def list_voters(
    candidate_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    last_updated: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Enforce multi-tenancy check
    if current_user.role != UserRole.ADMIN and current_user.candidate_id != candidate_id:
        raise HTTPException(status_code=403, detail="Unauthorized candidate access")
    
    query = db.query(Voter).filter(Voter.candidate_id == candidate_id)
    
    if last_updated:
        query = query.filter(Voter.updated_at > last_updated)
        
    return query.order_by(Voter.updated_at.asc()).offset(skip).limit(limit).all()

@app.post("/sync")
async def sync_voters(
    updates: List[VoterSyncUpdate], 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    results = {"success": [], "conflicts": []}
    for update in updates:
        voter = db.query(Voter).filter(Voter.id == update.id).first()
        if not voter:
            results["conflicts"].append({"id": update.id, "reason": "not_found"})
            continue

        # LWW - Last Write Wins based on version or timestamp
        # In this simplified version, we'll use version + updated_at comparison
        client_updated_at = datetime.fromisoformat(update.updated_at)
        
        if update.version > voter.version or (update.version == voter.version and client_updated_at > voter.updated_at):
            voter.status = update.status
            voter.sentiment = update.sentiment
            voter.notes = update.notes
            voter.version = update.version + 1
            voter.latitude = update.latitude
            voter.longitude = update.longitude
            voter.device_id = update.device_id
            voter.updated_at = client_updated_at
            results["success"].append(update.id)
        else:
            results["conflicts"].append({
                "id": update.id, 
                "reason": "older_version", 
                "server_version": voter.version,
                "server_updated_at": voter.updated_at.isoformat()
            })
    
    db.commit()
    return results

@app.get("/api/v1/extraction/review/{job_id}/excel")
async def export_job_review_excel(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR]))
):
    """
    Generates an Excel sheet for reviewing OCR extractions for a given job_id.
    """
    # 1. Verify job exists
    job = db.query(ExtractionJob).filter(ExtractionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 2. Fetch voters
    voters = db.query(Voter).filter(Voter.job_id == job_id).order_by(Voter.id.asc()).all()
    
    if not voters:
        raise HTTPException(status_code=404, detail="No extraction results found for this job")

    # 3. Prepare data for Excel
    data = []
    for voter in voters:
        s_data = voter.structured_data or {}
        
        # Combine relation names
        relation_name = ""
        if s_data.get("father_name"):
            relation_name = s_data.get("father_name")
        elif s_data.get("husband_name"):
            relation_name = s_data.get("husband_name")
        elif s_data.get("mother_name"):
            relation_name = s_data.get("mother_name")
            
        data.append({
            "Page No": s_data.get("page_num", ""),
            "EPIC ID": voter.voter_id,
            "Full Name": voter.full_name,
            "Relation Name": relation_name,
            "House No": s_data.get("house_no", ""),
            "Age": s_data.get("age", ""),
            "Gender": s_data.get("gender", "")
        })

    # 4. Create Excel in memory
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='OCR Review')
    
    output.seek(0)
    
    headers = {
        'Content-Disposition': f'attachment; filename="review_job_{job_id}.xlsx"'
    }
    
    return StreamingResponse(
        output, 
        headers=headers, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.get("/api/v1/extraction/jobs")
async def list_extraction_jobs_v1(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR]))
):
    """
    Returns a list of recent OCR jobs with record counts.
    """
    results = db.query(
        ExtractionJob.id,
        ExtractionJob.status,
        ExtractionJob.file_name,
        ExtractionJob.created_at,
        func.count(Voter.id).label("total_records")
    ).outerjoin(Voter, ExtractionJob.id == Voter.job_id)\
     .group_by(ExtractionJob.id)\
     .order_by(ExtractionJob.created_at.desc())\
     .all()
    
    return [
        {
            "id": r.id,
            "status": r.status,
            "filename": r.file_name,
            "created_at": r.created_at,
            "total_records": r.total_records
        } for r in results
    ]

@app.get("/api/v1/extraction/review/all/excel")
async def export_all_reviews_excel(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Aggregates all processed voter records into a single Excel file.
    """
    query = db.query(Voter, ExtractionJob.file_name).join(
        ExtractionJob, Voter.job_id == ExtractionJob.id
    )
    
    if start_date:
        query = query.filter(Voter.created_at >= start_date)
    if end_date:
        query = query.filter(Voter.created_at <= end_date)
        
    voters_with_jobs = query.order_by(ExtractionJob.created_at.desc(), Voter.id.asc()).all()
    
    if not voters_with_jobs:
        raise HTTPException(status_code=404, detail="No extraction results found")

    data = []
    for voter, file_name in voters_with_jobs:
        s_data = voter.structured_data or {}
        
        # Combine relation names
        relation_name = ""
        if s_data.get("father_name"):
            relation_name = s_data.get("father_name")
        elif s_data.get("husband_name"):
            relation_name = s_data.get("husband_name")
        elif s_data.get("mother_name"):
            relation_name = s_data.get("mother_name")
            
        data.append({
            "Document Name": file_name,
            "Page No": s_data.get("page_num", ""),
            "EPIC ID": voter.voter_id,
            "Full Name": voter.full_name,
            "Relation Name": relation_name,
            "House No": s_data.get("house_no", ""),
            "Age": s_data.get("age", ""),
            "Gender": s_data.get("gender", "")
        })

    # Create Excel in memory
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='All OCR Reviews')
    
    output.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="all_extraction_results.xlsx"'
    }
    
    return StreamingResponse(
        output, 
        headers=headers, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
