# app/zones.py
import cv2

ZONES = {
    1: {   # camera_id
        "restricted": {
            "type": "rectangle",
            "x1": 200,
            "y1": 750,
            "x2": 1000,
            "y2": 1050
        }
    },
    2: {   # camera_id
        "restricted": {
            "type": "rectangle",
            "x1": 700,
            "y1": 550,
            "x2": 1700,
            "y2": 1050
        }
    }
}

def point_in_rect(x, y, rect):
    return (
        rect["x1"] <= x <= rect["x2"] and
        rect["y1"] <= y <= rect["y2"]
    )

def draw_zone(frame, zone, label=None):
    if zone["type"] == "rectangle":
        x1, y1 = zone["x1"], zone["y1"]
        x2, y2 = zone["x2"], zone["y2"]

        # Draw rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # Optional label
        if label:
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

