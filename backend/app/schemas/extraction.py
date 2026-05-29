from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class CandidateBase(BaseModel):
    name: str
    party_name: Optional[str] = None
    constituency_code: str

class CandidateCreate(CandidateBase):
    pass

class CandidateResponse(CandidateBase):
    id: int
    logo_url: Optional[str] = None
    profile_image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class VoterBase(BaseModel):
    voter_id: str
    full_name: str
    structured_data: Dict[str, Any]
    confidence: float
    image_url: Optional[str] = None
    status: Optional[str] = "Pending"
    sentiment: Optional[str] = None
    notes: Optional[str] = None
    version: Optional[int] = 1
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class VoterSyncUpdate(BaseModel):
    id: int
    status: str
    sentiment: Optional[str] = None
    notes: Optional[str] = None
    version: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    device_id: str
    updated_at: str # ISO format

class VoterCreate(VoterBase):
    job_id: str
    raw_ocr_data: List[Dict[str, Any]]

class VoterResponse(VoterBase):
    id: int
    job_id: str
    status: str
    sentiment: Optional[str] = None
    notes: Optional[str] = None
    version: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class ExtractionJobBase(BaseModel):
    file_name: str
    status: str

class ExtractionJobResponse(ExtractionJobBase):
    id: str
    confidence_score: Optional[float] = None

    class Config:
        from_attributes = True
