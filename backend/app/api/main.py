import os
import uuid
import boto3
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from botocore.client import Config
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from celery_app import celery_app
from app.core.search import search_voters, create_index
from app.db.session import get_db, engine
from app.db.models import Base, Voter, User, UserRole
from app.schemas.extraction import VoterSyncUpdate, VoterResponse
from app.core.auth import (
    get_current_active_user, 
    require_role, 
    verify_password, 
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="OCR API")

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
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def root():
    return {"message": "OCR API is running"}

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.BOOTH_LEAD]))
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}_{file.filename}"
    
    try:
        # Upload to MinIO
        s3.upload_fileobj(file.file, MINIO_BUCKET_NAME, file_name)
        
        # Enqueue Celery task
        celery_app.send_task("process_document", args=[file_name, MINIO_BUCKET_NAME])
        
        return {
            "message": "File uploaded successfully",
            "file_name": file_name,
            "task_id": file_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search(
    q: str = Query(..., min_length=1), 
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    try:
        search_result = search_voters(q, limit)
        return {
            "results": search_result["results"],
            "transliterated": search_result["transliterated"],
            "user": current_user.username
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voters", response_model=List[VoterResponse])
async def list_voters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Voter).all()

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
