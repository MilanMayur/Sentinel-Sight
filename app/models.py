# app/models.py
from pydantic import BaseModel
from datetime import datetime

class CameraCreate(BaseModel):
    name: str
    location: str
    rtsp_url: str   # path to video file

class CameraOut(BaseModel):
    id: int
    name: str
    location: str | None = None
    rtsp_url: str
    status: str
    fps: float

    class Config:
        from_attributes = True

class EventOut(BaseModel):
    id: int
    camera_id: int
    timestamp: datetime
    rule: str
    object_type: str
    confidence: float
    bbox: str
    snapshot: str

    class Config:
        from_attributes = True
