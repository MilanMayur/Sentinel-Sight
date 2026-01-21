# app/inference.py
from ultralytics import YOLO
import cv2, os, time, torch
from app.rules import apply_rules
from app.zones import ZONES, draw_zone, point_in_rect
from fastapi.responses import StreamingResponse, Response 

latest_frames = {}
os.makedirs("snapshots", exist_ok=True)

def get_device():
    return "cuda" if torch.cuda.is_available() else "cpu"

device = get_device()
print(f"Using device: {device}")

def run_inference(camera_id, frame):
    if not hasattr(run_inference, "models"):
        run_inference.models = {}

    if camera_id not in run_inference.models:
        print(f"LOADING YOLO MODEL FOR CAMERA {camera_id}")
        run_inference.models[camera_id] = YOLO("yolov8n.pt").to("cuda")

    model = run_inference.models[camera_id]

    results = model.predict(frame, verbose=False)[0]
    print("DETECTIONS:", len(results.boxes))

    detections = []
    display_frame = frame.copy()

    if camera_id in ZONES:
        for zone_name, zone in ZONES[camera_id].items():
            draw_zone(display_frame, zone, label=zone_name)

    for box in results.boxes:
        cls = int(box.cls[0])
        label = model.names[cls]
        conf = float(box.conf[0])

        if label not in ("person", "car"):
            continue

        x1,y1,x2,y2 = map(int, box.xyxy[0])
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Check if inside restricted zone
        inside_zone = False
        if camera_id in ZONES:
            for zone in ZONES[camera_id].values():
                if zone["type"] == "rectangle" and point_in_rect(cx, cy, zone):
                    inside_zone = True
                    break

        detections.append({
            "label": label,
            "conf": conf,
            "bbox": [x1,y1,x2,y2]
        })

        if label == "car":
            color = (255, 0, 0)   # Blue for cars
        elif inside_zone:
            color = (0, 165, 255) # Orange
        else:
            color = (0, 255, 0)   # Green

        cv2.rectangle(display_frame,(x1,y1),(x2,y2),color,2)
        cv2.putText(display_frame,f"{label} {conf:.2f}",(x1,y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX,0.6,color,2)

    display_frame = cv2.resize(display_frame, (960, 540)) 
    latest_frames[camera_id] = display_frame
    apply_rules(camera_id, display_frame, detections)

def frame_stream(camera_id: int):
    def gen():
        while True:
            if camera_id in latest_frames:
                frame = latest_frames[camera_id]
                ret, jpeg = cv2.imencode(".jpg", frame)
                if ret:
                    yield (b"--frame\r\n"
                            b"Content-Type: image/jpeg\r\n\r\n" + 
                            jpeg.tobytes() + b"\r\n")
            time.sleep(0.05)
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")

def get_latest_frame(camera_id: int):
    if camera_id not in latest_frames:
        return Response(status_code=404)

    frame = latest_frames[camera_id]
    ret, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    if not ret:
        return Response(status_code=500)

    return Response(jpeg.tobytes(), media_type="image/jpeg")

