# RESEARCH.md - Research & Best Practices
This document summarizes the research conducted on global video management and AI video analytics platforms, the design patterns adopted in SentinelSight, and the roadmap for future improvements.

## 1 - Platforms Studied:
The following real-world platforms were studied to extract architectural and product-level best practices.

### A - Milestone Systems (VMS)
#### What it is
- Enterprise-grade Video Management System (VMS)
- Focus on camera lifecycle, reliability, and operator workflows
#### Key Observations
- Cameras are first-class entities with persistent configuration
- Streams auto-recover on restart or failure
- Clear separation between:
  - Video ingestion
  - Analytics modules
  - Operator interfaces
#### Adopted in SentinelSight
- Persistent camera registry (SQLite-backed)
- Auto-restart ingestion on backend startup
- Camera health metadata (status, FPS, last frame time)
- Modular separation between ingestion, inference, and rules
---

### B - BriefCam (Analytics Modules)
#### What it is
- AI video analytics platform focused on post-incident analysis
- Organizes analytics into Review, Respond, Research
#### Key Observations
- Events are more important than raw video
- Metadata-driven workflows enable fast search and filtering
- Clear distinction between:
  - Real-time alerts
  - Historical analysis
#### Adopted in SentinelSight
- Event-centric architecture
- Structured event schema:
  - camera_id
  - rule
  - confidence
  - timestamp
  - snapshot reference
- Event feed filtered by camera
- /events/{id} API for event drill-down (even if UI uses summary view)
---

### C - Avigilon (AI-Driven Operations)
#### What it is
- End-to-end AI-powered video security platform
- Focus on reducing operator overload
#### Key Observations
- Avoid alert flooding
- One alert per meaningful incident
- Emphasis on operator-friendly review
#### Adopted in SentinelSight
- Intrusion events trigger once per zone entry
- Loitering events are time-based and stateful
- Snapshot de-duplication per incident
- Horizontal event card layout to improve visual scanning
---

### D - Frigate (Local-First & Privacy)
#### What it is
- Open-source NVR with local AI inference
- Strong emphasis on privacy and storage efficiency
#### Key Observations
- Local inference over cloud-first processing
- Avoid storing full video continuously
- Event-driven snapshot and clip generation
- Config-driven zones and rules
#### Adopted in SentinelSight
- Local-only inference (YOLO)
- No continuous video storage
- Event-driven snapshots only
- Per-camera snapshot retention
- Graceful handling of expired media in UI
- JSON-based zone configuration

## 2 - Best Practices Adopted:
### Architecture
- Modular monolith (ingestion → inference → rules → events)
- Clear separation of concerns
- Thread-per-camera ingestion model (MVP-safe)
### Data Management
- Event metadata persists longer than media
- Per-camera snapshot directories
- Retention policies enforced per camera
- Database treated as source of truth for events
### Performance & Stability
- FPS-aware ingestion pacing
- Auto-reconnect on stream failure
- Lightweight polling-based dashboard
- GPU acceleration when available, CPU fallback otherwise
### Security & Privacy
- Local-first processing
- No raw video archival
- Minimal data persistence
- Explicit documentation of limitations

## 3 - Features Deliberately Scoped Out (MVP Decisions):
The following features were intentionally excluded to keep the MVP focused and stable:
- Person re-identification/tracking IDs
- Role-based access control
- Multi-tenant user management
- Distributed deployment
- Event clip recording (pre/post)
- Message brokers (MQTT / Kafka)

## 2–3 Week Roadmap:
If given additional time, the next priorities would be:
- Object Tracking
  - Stable IDs across frames
  - More accurate loitering logic
- Event Clips
  - Short pre/post video segments
  - Operator-friendly playback
- RBAC
  - Admin / Operator / Viewer roles
  - Audit logging
- Messaging & Integrations
  - External system integrations
- Scalability Enhancements
  - Multi-model deployment
 
## Summary:
SentinelSight’s design intentionally mirrors real-world VMS and AI analytics platforms, balancing:
- Engineering simplicity
- Operator usability
- Privacy awareness
- Scalability readiness

The platform demonstrates how production-grade patterns can be implemented in a minimal, working MVP, while leaving a clear path toward enterprise-scale evolution.
