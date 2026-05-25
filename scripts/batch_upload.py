import os
import requests
import glob

API_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"
FILES_PATTERN = "benchmarks/data/raw/*.pdf"

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
    
    files = glob.glob(FILES_PATTERN)
    print(f"Found {len(files)} files to upload.")
    
    for file_path in files:
        file_name = os.path.basename(file_path)
        print(f"Uploading {file_name}...", end=" ", flush=True)
        with open(file_path, "rb") as f:
            upload_response = requests.post(
                f"{API_URL}/upload",
                headers=headers,
                files={"file": (file_name, f, "application/pdf")}
            )
        if upload_response.status_code == 200:
            print("SUCCESS")
        else:
            print(f"FAILED: {upload_response.text}")

if __name__ == "__main__":
    main()
