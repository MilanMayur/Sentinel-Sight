# ui/dashboard.py
import streamlit as st
import requests, time, os 

API = "http://127.0.0.1:8000"
REFRESH_SEC = 0.5

st.set_page_config(page_title="SentinelSight", layout="wide")
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 3rem;
    }
    .fixed-header {
        position: fixed;
        top: 100;
        left: 10;
        width: 100%;
        background-color: #0e1117;
        z-index: 999;
        padding: 10px 0px;
        border-bottom: 1px solid #333;
    }
    .content {
        margin-top: 100px;
    }
    </style>

    <div class="fixed-header">
        <h2>SentinelSight - AI Video Analytics Platform</h2>
    </div>

    <div class="content">
    """,
    unsafe_allow_html=True
)

def try_get(url):
    try:
        return requests.get(url, timeout=2)
    except:
        return None

# Try to load cameras
resp = try_get(f"{API}/cameras")

if resp is None:
    st.warning("🔄 Server not reachable. Retrying...")
    time.sleep(REFRESH_SEC)
    st.rerun()

cams = resp.json()

# Sidebar
st.sidebar.header("Cameras")

if not cams:
    st.sidebar.info("No cameras added yet")
    st.stop()

camera_map = {c["id"]: c for c in cams}
camera_id = st.sidebar.selectbox("Select Camera", list(camera_map.keys()))

cam = camera_map[camera_id]
st.sidebar.write(f"🎥 Cam- {cam['name']}")
st.sidebar.write(f"📍 Loc- {cam['location']}")
st.sidebar.write(f"📡 Status- {cam['status']}")
st.sidebar.write(f"🎞️ FPS: {cam['fps']}")

# Live Video 
st.header("Live Video (AI Overlay)")
frame_resp = requests.get(f"{API}/frame/{camera_id}")

if frame_resp.status_code == 200:
    st.image(frame_resp.content, width=1000)
else:
    st.info("Waiting for first frame...")

# Events 
st.header("Event Feed")

events_resp = try_get(f"{API}/events?camera_id={camera_id}")

if events_resp:
    events = events_resp.json()
    if not events:
        st.info("No events for this camera")
    else:
        cols_per_row = 3  # number of events per row

        for i in range(0, len(events[:15]), cols_per_row):
            cols = st.columns(cols_per_row)

            for col, e in zip(cols, events[i:i+cols_per_row]):
                with col:
                    st.subheader(e["rule"].upper())

                    snapshot_path = e.get("snapshot")
                    if snapshot_path and os.path.exists(snapshot_path):
                        st.image(snapshot_path, width='stretch')
                    else:
                        st.caption("📁 Snapshot expired")

                    st.caption(f"Confidence: {e['confidence']:.2f}")
                    st.caption(f"Time: {e['timestamp']}")
else:
    st.warning("Unable to load events")

# Auto Refresh
time.sleep(REFRESH_SEC)
st.rerun()

st.markdown("</div>", unsafe_allow_html=True)