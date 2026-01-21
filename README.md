# Sentinel Sight
SentinelSight is a local-first, event-driven AI video analytics platform. It ingests multiple camera streams, performs real-time computer vision inference, applies rule-based analytics (intrusion & loitering), and presents results through a lightweight operator dashboard.

# Images
<img width="1922" height="949" alt="Screenshot (130)" src="https://github.com/user-attachments/assets/60ca3a7e-11ab-440c-924e-8819ad298915" />
<img width="1927" height="949" alt="Screenshot (131)" src="https://github.com/user-attachments/assets/af805957-e7de-4765-87c8-78b64edf1363" />



## Features
### Core Capabilities
- Multi-camera ingestion (RTSP or video files)
- AI-based object detection (YOLOv8) (person and car)
- Zone-based analytics
- Intrusion detection
- Loitering detection (time-based)
- Event generation with confidence & timestamps
- Snapshot evidence with per-camera retention
- Camera health & FPS metrics
- Auto-recovery of camera streams

### Dashboard
- Camera list & status
- Live video with AI overlays
- Context-aware event feed (per camera)
- Snapshot preview with graceful handling of expired media

## Architecture
```
sentinelsight/
├── app/
│   ├── main.py          # FastAPI app & routes
│   ├── ingestion.py     # Video ingestion & stream management
│   ├── inference.py     # AI inference & frame annotation
│   ├── rules.py         # Zone + intrusion + loitering logic
│   ├── zones.py         # Zone definitions & helpers
│   ├── database.py      # SQLite models
│   ├── models.py        # Pydantic schemas
│   ├── storage.py       # Snapshot retention logic
│
├── ui/
│   └── dashboard.py     # Streamlit dashboard
│
├── snapshots/           # Per-camera snapshot storage
├── sentinelsight.db     # SQLite database
```
## Tech Stack
- Backend: FastAPI, SQLAlchemy, SQLite
- AI / CV: Ultralytics YOLOv8, OpenCV
- Frontend: Streamlit
- Storage: Local filesystem with retention policies
- Runtime: Python 3.10+

## How to Run
```
# 1- Install Dependencies
pip install -r requirements.txt

# 2- Start Backend (FastAPI)
python -m uvicorn app.main:app
```
The backend will:
- Initialize the database
- Restore cameras from DB
- Automatically restart ingestion pipelines

```
# 3- Start Dashboard (Streamlit)
streamlit run ui/dashboard.py
```

### Adding a Camera
You can add cameras via REST API.
```
Invoke-RestMethod -Uri http://127.0.0.1:8000/cameras `
-Method POST `
-Headers @{ "Content-Type"="application/json" } `
-Body '{
  "name": "Street",
  "location": "HQ",
  "rtsp_url": "videos/video1.mp4"
}'
```

### Event Types
- Intrusion
  - Triggered when a person enters a restricted zone
  - Fired once per zone entry
- Loitering
  - Triggered when a person remains in a zone longer than a configurable threshold
  - Fired once per loitering episode
 
Each event includes:
- Camera ID
- Timestamp
- Rule type
- Object type
- Confidence score
- Snapshot path

### Snapshot Storage & Retention
Snapshots are stored per camera:
```
snapshots/camera_1/
snapshots/camera_2/
```
- Retention is enforced per camera
- Old snapshots are automatically deleted
- Event metadata may outlive snapshot files
- UI gracefully handles expired snapshots

### API Endpoints
- Cameras
```
POST /cameras
GET /cameras
DELETE /cameras/{camera_id}
```
- Events
```
GET /events
GET /events/{event_id}
```
- Live
```
GET /frame/{camera_id}
```

## Testing the System
1 - Add a camera (video file)\
2 - Define a restricted zone (JSON-based)\
3 - Start backend and dashboard\
4 - Observe:
  - Live video with overlays
  - Intrusion alerts when entering zone
  - Loitering alerts after threshold
  - Events appearing in dashboard

## Future Improvements
- Person tracking for precise loitering
- Event clip recording (pre/post seconds)
- Role-based access control
- Multi-site grouping

