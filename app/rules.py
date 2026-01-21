# app/rules.py
from datetime import datetime, timedelta
import cv2, os
from app.database import SessionLocal, Event
from app.zones import ZONES, point_in_rect
from app.storage import cleanup_snapshots

loiter_state = {}
intrusion_state = {}
snapshot_state = set()
LOITER_THRESHOLD_SECONDS = 10

def apply_rules(camera_id, frame, detections):
    if not detections:
        return
    
    if camera_id not in ZONES:
        return
    
    zones = ZONES[camera_id]
    now = datetime.utcnow()
    db = SessionLocal()

    for zone_name, zone in zones.items():
        person_in_zone = False

        for d in detections:
            if d["label"] != "person":
                continue

            x1, y1, x2, y2 = d["bbox"]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            if zone["type"] == "rectangle" and point_in_rect(cx, cy, zone):
                person_in_zone = True
                key = (camera_id, zone_name)

                # Intrusion
                if key not in intrusion_state:
                    intrusion_state[key] = True
                    snap_key = (camera_id, zone_name, "intrusion")
                    if snap_key not in snapshot_state:
                        snapshot_state.add(snap_key)
                        save_event(db, camera_id, "intrusion", d, frame)

                # Loitering
                if key not in loiter_state:
                    loiter_state[key] = now
                else:
                    duration = (now - loiter_state[key]).total_seconds()
                    if duration >= LOITER_THRESHOLD_SECONDS:
                        snap_key = (camera_id, zone_name, "loitering")
                        if snap_key not in snapshot_state:
                            snapshot_state.add(snap_key)
                            save_event(db, camera_id, "loitering", d, frame)
                        loiter_state[key] = now + timedelta(seconds=10)

                break

        # Reset if zone is empty
        if not person_in_zone:
            loiter_state.pop((camera_id, zone_name), None)
            intrusion_state.pop((camera_id, zone_name), None)
            snapshot_state.discard((camera_id, zone_name, "intrusion"))
            snapshot_state.discard((camera_id, zone_name, "loitering"))

    db.commit()
    db.close()

def save_event(db, camera_id, rule, d, frame):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")

    camera_dir = f"snapshots/camera_{camera_id}"
    os.makedirs(camera_dir, exist_ok=True)
    path = f"{camera_dir}/{rule}_{ts}.jpg"

    cv2.imwrite(path, frame)
    cleanup_snapshots(camera_id)

    ev = Event(
        camera_id=camera_id,
        rule=rule,
        object_type=d["label"],
        confidence=d["conf"],
        bbox=str(d["bbox"]),
        snapshot=path
    )
    db.add(ev)

