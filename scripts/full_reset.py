import os
import sys

# Add backend to path to import models
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.session import SessionLocal
from app.db.models import ExtractionJob, Voter, AuditLog

def full_reset():
    db = SessionLocal()
    try:
        print("Clearing all data from database...")
        db.query(Voter).delete()
        db.query(AuditLog).delete()
        db.query(ExtractionJob).delete()
        db.commit()
        print("Database reset successful.")
    except Exception as e:
        print(f"Error resetting database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    full_reset()
