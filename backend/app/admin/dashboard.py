import streamlit as st
import pandas as pd
import requests
import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import ExtractionJob, Voter, JobStatus
from app.core.audit import log_action
from app.core.search import index_voter
import json

st.set_page_config(page_title="OCR HITL Dashboard", layout="wide")
API_URL = os.getenv("API_URL", "http://api:8000")

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        username = st.session_state["username"]
        password = st.session_state["password"]
        
        # Request JWT token from API
        try:
            response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
            if response.status_code == 200:
                token = response.json().get("access_token")
                st.session_state["jwt_token"] = token
                st.session_state["password_correct"] = True
                del st.session_state["password"]
            else:
                st.session_state["password_correct"] = False
        except Exception as e:
            st.error(f"Failed to connect to API for authentication: {e}")
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Login incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

def get_auth_headers():
    token = st.session_state.get("jwt_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass # We will close it manually or use context manager

st.title("Human-In-The-Loop OCR Review")

db = get_db()

# Fetch jobs pending review
pending_jobs = db.query(ExtractionJob).filter(ExtractionJob.status == JobStatus.PENDING_REVIEW).all()

if not pending_jobs:
    st.info("No jobs pending review.")
else:
    job_options = {f"{j.id} - {j.file_name}": j.id for j in pending_jobs}
    selected_job_label = st.selectbox("Select a job to review", list(job_options.keys()))
    selected_job_id = job_options[selected_job_label]

    job = db.query(ExtractionJob).filter(ExtractionJob.id == selected_job_id).first()
    voters = db.query(Voter).filter(Voter.job_id == selected_job_id).all()

    st.subheader(f"Reviewing Job: {job.file_name}")
    st.write(f"Confidence Score: {job.confidence_score:.2f}")

    updated_voters = []
    
    for voter in voters:
        with st.expander(f"Voter: {voter.full_name} ({voter.voter_id}) - Confidence: {voter.confidence:.2f}"):
            # Display Image Snippet if available
            if voter.image_url:
                try:
                    # In production, we'd generate a signed URL from S3/MinIO
                    # For local dev, we fetch it or use the path
                    st.image(voter.image_url, caption="OCR Snippet", use_column_width=False, width=400)
                except Exception as e:
                    st.warning(f"Could not load image snippet: {e}")
            else:
                st.info("No visual snippet available for this record.")

            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Full Name", value=voter.full_name, key=f"name_{voter.id}")
                new_voter_id = st.text_input("Voter ID", value=voter.voter_id, key=f"id_{voter.id}")
            
            with col2:
                structured_data_str = st.text_area("Structured Data (JSON)", 
                                                 value=json.dumps(voter.structured_data, indent=2, ensure_ascii=False),
                                                 key=f"data_{voter.id}")
            
            try:
                new_structured_data = json.loads(structured_data_str)
            except json.JSONDecodeError:
                st.error("Invalid JSON in Structured Data")
                new_structured_data = voter.structured_data

            if new_name != voter.full_name or new_voter_id != voter.voter_id or new_structured_data != voter.structured_data:
                updated_voters.append({
                    "voter_obj": voter,
                    "old_name": voter.full_name,
                    "new_name": new_name,
                    "old_voter_id": voter.voter_id,
                    "new_voter_id": new_voter_id,
                    "old_data": voter.structured_data,
                    "new_data": new_structured_data
                })

    if st.button("Approve and Finalize Job"):
        # Save changes and log them
        for item in updated_voters:
            v = item["voter_obj"]
            
            # Precise Audit Log: Old JSON vs New JSON
            old_val = {
                "full_name": item["old_name"],
                "voter_id": item["old_voter_id"],
                "structured_data": item["old_data"]
            }
            new_val = {
                "full_name": item["new_name"],
                "voter_id": item["new_voter_id"],
                "structured_data": item["new_data"]
            }

            log_action(
                db, 
                action="manual_correction", 
                target_type="voter", 
                target_id=str(v.id),
                old_value=old_val,
                new_value=new_val
            )

            # Update voter
            v.full_name = item["new_name"]
            v.voter_id = item["new_voter_id"]
            v.structured_data = item["new_data"]
        
        # Update job status to COMPLETED to align with state machine
        job.status = JobStatus.COMPLETED
        db.commit()

        # Index to Elasticsearch
        for voter in voters:
            index_voter(
                voter_id=voter.voter_id,
                full_name=voter.full_name,
                job_id=voter.job_id,
                confidence=voter.confidence,
                structured_data=voter.structured_data
            )
        
        st.success(f"Job {job.id} approved and indexed to Elasticsearch!")
        st.rerun()

db.close()
