# SentinelSight Live Demo Script
SentinelSight is a local-first AI video analytics platform that ingests multiple camera streams, runs real-time computer vision, applies zone-based rules, and generates actionable events through a web dashboard.

## Setup (Before Demo)
Start Backend
```
python -m uvicorn app.main:app
```
Start Dashboard
```
streamlit run ui/dashboard.py
```
Ensure:
- Backend is running on http://127.0.0.1:8000
- Dashboard opens in browser

## Demo Flow
### Step 1 - Camera Management
Action
- Open the dashboard
- The camera list is in the sidebar
- Features of sidebar:
  - Camera name
  - Location
  - Status (online/offline)
  - FPS

### Step 2 - Live Video with AI Overlay
Action
- Select a camera from the sidebar
- Watch live video feed
- Highlight:
  - Bounding boxes on people
  - Color coding:
    - Green → normal detection
    - Orange → restricted zone
    - Blue → vehicles (if visible)
  - Zone overlay drawn on the frame
 
### Step 3 - Intrusion/Loitering Detection
Action
- Let a person enter a restricted zone in the video
- Wait for an INTRUSION/LOITERING event to appear in Event Feed
- Snapshots with rule, timestamp and confidence score appears

### Step 4 - Event Review & Retention
Action
- Scroll through the Event Feed
- Multiple events appear horizontally


