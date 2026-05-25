import os
import requests
import sys

API_URL = "http://localhost:8000"
AUTH_DATA = {"username": "admin", "password": "admin123"}

def upload_file(filepath):
    print(f"Logging in to {API_URL}...")
    try:
        res = requests.post(f"{API_URL}/token", data=AUTH_DATA)
        if res.status_code != 200:
            print(f"Failed to login: {res.text}")
            return
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return

    if not os.path.exists(filepath):
        print(f"File {filepath} not found.")
        return

    filename = os.path.basename(filepath)
    print(f"Uploading {filename}...")
    with open(filepath, 'rb') as f:
        files_payload = {'file': (filename, f, 'application/pdf')}
        res = requests.post(f"{API_URL}/upload", headers=headers, files=files_payload)
        if res.status_code == 200:
            print(f"  Successfully uploaded {filename}. Task ID: {res.json().get('task_id')}")
        else:
            print(f"  Failed to upload {filename}: {res.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_file.py <filepath>")
    else:
        upload_file(sys.argv[1])
