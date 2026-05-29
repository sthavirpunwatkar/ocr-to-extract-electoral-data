import os
import requests
import glob

API_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"
FILES_PATTERN = "benchmarks/data/raw/**/*.pdf"

def main():
    # Get token
    response = requests.post(
        f"{API_URL}/token",
        data={"username": USERNAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code != 200:
        print(f"Failed to get token: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get first candidate
    candidates_response = requests.get(f"{API_URL}/candidates", headers=headers)
    if candidates_response.status_code != 200 or not candidates_response.json():
        # Create a default candidate if none exists
        print("No candidates found, creating default...")
        create_res = requests.post(
            f"{API_URL}/candidates",
            headers=headers,
            json={"name": "Campaign 2026", "party_name": "Independent", "constituency_code": "MH01"}
        )
        candidate_id = create_res.json()["id"]
    else:
        candidate_id = candidates_response.json()[0]["id"]
    
    print(f"Using Candidate ID: {candidate_id}")
    
    files = glob.glob(FILES_PATTERN, recursive=True)
    print(f"Found {len(files)} files to upload.")
    
    for file_path in files:
        file_name = os.path.basename(file_path)
        print(f"Uploading {file_name}...", end=" ", flush=True)
        with open(file_path, "rb") as f:
            upload_response = requests.post(
                f"{API_URL}/upload",
                headers=headers,
                params={"candidate_id": candidate_id},
                files={"file": (file_name, f, "application/pdf")}
            )
        if upload_response.status_code == 200:
            print("SUCCESS")
        else:
            print(f"FAILED: {upload_response.text}")

if __name__ == "__main__":
    main()
