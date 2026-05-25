# Campaign Mobile App

## Offline Data Strategy
The app uses `sqflite` for local data persistence. All changes made while offline are saved locally with an `is_synced` flag set to `0`.

## Sync Flow
1. **Fetch:** When online, the app fetches the latest voter data from the backend via `GET /voters` and updates the local database.
2. **Local Update:** User edits a voter's status or location. These are saved locally with `is_synced = 0` and an updated `timestamp`.
3. **Sync Push:** When the user clicks the sync button:
   - The app collects all records where `is_synced = 0`.
   - It sends a batch `POST /sync` request to the backend.
   - The payload includes `id`, `status`, `version`, `latitude`, `longitude`, `device_id`, and `updated_at`.
4. **Backend Processing:** The backend performs conflict resolution and returns a list of successfully synced IDs and conflicts.
5. **Local Mark:** The app marks successfully synced records as `is_synced = 1`.

## Conflict Resolution Strategy: LWW (Last Write Wins)
The backend uses a version-based and timestamp-based LWW strategy:
- If the incoming record has a higher `version` than the server, it wins.
- If versions are equal, the record with the later `updated_at` timestamp wins.
- If the server record is "fresher", a conflict is returned, and the client should ideally re-fetch or prompt the user (currently just logged).

## GIS Integration
The app uses the `geolocator` package to capture GPS coordinates (latitude and longitude) during voter verification. This data is synced to the backend for spatial analysis in future phases.
