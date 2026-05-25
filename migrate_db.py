import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres_password@localhost:5432/ocr_db")

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Checking for image_url column...")
        # Check if column exists
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='voters' AND column_name='image_url'"))
        if not result.fetchone():
            print("Adding image_url column to voters table...")
            conn.execute(text("ALTER TABLE voters ADD COLUMN image_url VARCHAR"))
            conn.commit()
            print("Migration successful.")
        else:
            print("Column image_url already exists.")

if __name__ == "__main__":
    migrate()
