# app/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

engine = create_engine(
    "sqlite:///sentinelsight.db",
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(String)
    rtsp_url = Column(String)
    status = Column(String, default="offline")
    fps = Column(Float, default=0)
    last_frame_time = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    camera_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    rule = Column(String)
    object_type = Column(String)
    confidence = Column(Float)
    bbox = Column(String)
    snapshot = Column(String)

def init_db():
    Base.metadata.create_all(engine)
