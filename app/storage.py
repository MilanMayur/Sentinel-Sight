# app/storage.py
from pathlib import Path

BASE_SNAPSHOT_DIR = Path("snapshots")
MAX_SNAPSHOTS = 1000  

def cleanup_snapshots(camera_id: int):
    camera_dir = BASE_SNAPSHOT_DIR / f"camera_{camera_id}"

    if not camera_dir.exists():
        return

    files = sorted(
        camera_dir.glob("*.jpg"),
        key=lambda f: f.stat().st_mtime
    )

    if len(files) <= MAX_SNAPSHOTS:
        return

    for f in files[:-MAX_SNAPSHOTS]:
        try:
            f.unlink()
        except:
            pass
