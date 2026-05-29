import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ocr_user:ocr_password@localhost:5432/ocr_db")

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Checking for image_url column in voters...")
        # Check if image_url exists in voters
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='voters' AND column_name='image_url'"))
        if not result.fetchone():
            print("Adding image_url column to voters table...")
            conn.execute(text("ALTER TABLE voters ADD COLUMN image_url VARCHAR"))
            conn.commit()
            print("image_url added successfully.")
        else:
            print("Column image_url already exists in voters.")

        print("Checking for candidate_id column in voters...")
        # Check if candidate_id exists in voters
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='voters' AND column_name='candidate_id'"))
        if not result.fetchone():
            print("Adding candidate_id column to voters table...")
            # We assume candidates table exists or will be created
            conn.execute(text("ALTER TABLE voters ADD COLUMN candidate_id INTEGER"))
            conn.commit()
            print("candidate_id added successfully to voters.")
        else:
            print("Column candidate_id already exists in voters.")

        print("Checking for candidate_id column in extraction_jobs...")
        # Check if candidate_id exists in extraction_jobs
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='extraction_jobs' AND column_name='candidate_id'"))
        if not result.fetchone():
            print("Adding candidate_id column to extraction_jobs table...")
            conn.execute(text("ALTER TABLE extraction_jobs ADD COLUMN candidate_id INTEGER"))
            conn.commit()
            print("candidate_id added successfully to extraction_jobs.")
        else:
            print("Column candidate_id already exists in extraction_jobs.")

        print("Checking for candidate_id column in users...")
        # Check if candidate_id exists in users
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='candidate_id'"))
        if not result.fetchone():
            print("Adding candidate_id column to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN candidate_id INTEGER"))
            conn.commit()
            print("candidate_id added successfully to users.")
        else:
            print("Column candidate_id already exists in users.")

if __name__ == "__main__":
    migrate()
