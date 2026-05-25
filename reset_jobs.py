from backend.app.db.session import SessionLocal
from backend.app.db.models import ExtractionJob, JobStatus

def reset_jobs():
    db = SessionLocal()
    try:
        # Update all COMPLETED jobs to PENDING_REVIEW for demonstration purposes
        jobs = db.query(ExtractionJob).filter(ExtractionJob.status == JobStatus.COMPLETED).all()
        print(f"Resetting {len(jobs)} jobs to PENDING_REVIEW...")
        for job in jobs:
            job.status = JobStatus.PENDING_REVIEW
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    reset_jobs()
