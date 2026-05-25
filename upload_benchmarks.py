import requests
import os
import time

API_URL = "http://127.0.0.1:8000"
USERNAME = "admin"
PASSWORD = "admin123"
RAW_DATA_DIR = "benchmarks/data/raw"

def get_token():
    print(f"Logging in as {USERNAME}...")
    response = requests.post(
        f"{API_URL}/token",
        data={"username": USERNAME, "password": PASSWORD}
    )
    response.raise_for_status()
    return response.json()["access_token"]

def upload_file(file_path, token):
    file_name = os.path.basename(file_path)
    print(f"Uploading {file_name}...")
    
    with open(file_path, "rb") as f:
        files = {"file": (file_name, f, "application/pdf")}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_URL}/upload",
            headers=headers,
            files=files
        )
    
    if response.status_code == 200:
        print(f"Successfully uploaded {file_name}. Task ID: {response.json().get('task_id')}")
    else:
        print(f"Failed to upload {file_name}: {response.text}")

def main():
    try:
        token = get_token()
        files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".pdf")]
        print(f"Found {len(files)} files to upload.")
        
        for filename in files:
            file_path = os.path.join(RAW_DATA_DIR, filename)
            upload_file(file_path, token)
            # Small delay to prevent overwhelming the queue immediately
            time.sleep(0.5)
            
        print("\nAll files have been submitted to the processing queue.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
