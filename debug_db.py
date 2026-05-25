from backend.app.db.session import SessionLocal
from backend.app.db.models import ExtractionJob, Voter, JobStatus

def check_db():
    db = SessionLocal()
    try:
        jobs = db.query(ExtractionJob).all()
        print(f"Total jobs: {len(jobs)}")
        for job in jobs:
            print(f"Job ID: {job.id}, File: {job.file_name}, Status: {job.status}, Confidence: {job.confidence_score}")
            
        voters = db.query(Voter).all()
        print(f"Total voters: {len(voters)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
