# app/ingestion.py
import cv2, threading, time
from datetime import datetime
from app.database import SessionLocal, Camera
from app.inference import run_inference

threads = {}

def start_ingestion(camera):
    if camera.id in threads and threads[camera.id] is not None:
        return  # already running

    t = threading.Thread(
        target=ingest_loop,
        args=(camera.id, camera.rtsp_url),
        daemon=True
    )
    threads[camera.id] = t
    t.start()

def ingest_loop(camera_id, rtsp_url):
    print("INGESTION STARTED FOR CAMERA", camera_id)

    cap = cv2.VideoCapture(rtsp_url)
    db = SessionLocal()

    source_fps = cap.get(cv2.CAP_PROP_FPS)
    if source_fps <= 0:
        source_fps = 10  # fallback

    frame_interval = 1.0 / source_fps

    frame_count = 0
    fps_start = time.time()

    while threads.get(camera_id) is not None:
        ok, frame = cap.read()
        if not ok:
            time.sleep(3)
            cap = cv2.VideoCapture(rtsp_url)
            continue

        start = time.time()
        run_inference(camera_id, frame)
        elapsed = time.time() - start
        sleep_time = max(0, frame_interval - elapsed)
        time.sleep(sleep_time)

        frame_count += 1
        now = time.time()

        # Update FPS every 1 second
        if now - fps_start >= 1.0:
            fps = frame_count / (now - fps_start)

            cam = db.query(Camera).get(camera_id)
            if cam:
                cam.fps = round(fps, 2)
                cam.last_frame_time = datetime.utcnow()
                db.commit()

            frame_count = 0
            fps_start = now

    cap.release()
    db.close()
    print("INGESTION STOPPED FOR CAMERA", camera_id)

def stop_ingestion(camera_id):
    threads[camera_id] = None   # flag

