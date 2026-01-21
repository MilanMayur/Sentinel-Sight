# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import init_db, SessionLocal, Camera, Event
from app.models import CameraCreate, CameraOut, EventOut
from app.ingestion import start_ingestion, stop_ingestion
from app.inference import frame_stream, get_latest_frame

app = FastAPI(title="SentinelSight")

@app.on_event("startup")
def startup():
    init_db()
    db = SessionLocal()
    cameras = db.query(Camera).all()
    for cam in cameras:
        start_ingestion(cam)
    db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health") 
def health(): 
    return {"status": "ok"}

@app.post("/cameras", response_model=CameraOut) # Manual API call only for camera addition
def add_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    cam = Camera(**camera.dict(), status="online")
    db.add(cam)
    db.commit()
    db.refresh(cam)
    start_ingestion(cam)
    return cam
#-----------------------------------------------------------------------
@app.get("/cameras", response_model=list[CameraOut])
def get_cameras(db: Session = Depends(get_db)):
    return db.query(Camera).all()

@app.get("/frame/{camera_id}") # Live preview
def frame(camera_id: int):
    return get_latest_frame(camera_id)

@app.get("/events", response_model=list[EventOut])
def get_events(
    camera_id: int | None = Query(default=None),
    db: Session = Depends(get_db)
):
    q = db.query(Event)
    if camera_id is not None:
        q = q.filter(Event.camera_id == camera_id)

    return q.order_by(Event.timestamp.desc()).all()
#-----------------------------------------------------------------------
@app.get("/events/{event_id}", response_model=EventOut) # not used by dashboard
def get_event(event_id: int, db: Session = Depends(get_db)):
    return db.query(Event).get(event_id)

@app.delete("/cameras/{camera_id}") # Manual API call only for camera deletion
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    cam = db.query(Camera).get(camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")

    stop_ingestion(camera_id)
    db.delete(cam)
    db.commit()
    return {"status": "deleted"}

