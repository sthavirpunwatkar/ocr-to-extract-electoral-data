from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    SUPERVISOR = "Supervisor"
    BOOTH_LEAD = "Booth Lead"
    FIELD_WORKER = "Field Worker"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FIELD_WORKER, nullable=False)
    is_active = Column(Boolean, default=True)

class JobStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"

class ExtractionJob(Base):
    __tablename__ = "extraction_jobs"

    id = Column(String, primary_key=True)
    file_name = Column(String, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    confidence_score = Column(Float, nullable=True)
    meta_data = Column(JSONB, nullable=True)  # Added to satisfy JSONB requirement
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    error_message = Column(String, nullable=True)

class Voter(Base):
    __tablename__ = "voters"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("extraction_jobs.id"))
    voter_id = Column(String, index=True)
    full_name = Column(String)
    structured_data = Column(JSONB)  # Updated to JSONB
    raw_ocr_data = Column(JSONB)      # Updated to JSONB
    confidence = Column(Float)
    image_url = Column(String, nullable=True) # Path to the snippet in MinIO
    status = Column(String, default="Pending") # Visited, Confirmed, etc.
    sentiment = Column(String, nullable=True) # Supportive, Neutral, Opposed
    notes = Column(String, nullable=True)
    version = Column(Integer, default=1)
    device_id = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=False) # e.g., 'voter'
    target_id = Column(String, nullable=False)
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
