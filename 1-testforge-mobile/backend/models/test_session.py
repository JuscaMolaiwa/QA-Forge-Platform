import enum
from datetime import datetime, timezone
from extensions import db
import json

class SessionStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    CANCELLED = "cancelled"

class TestSession(db.Model):
    __tablename__ = "test_sessions"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True)
    test_name = db.Column(db.String(256), nullable=False)
    test_file = db.Column(db.String(512), nullable=True)
    test_content = db.Column(db.Text, nullable=True)
    app_path = db.Column(db.String(512), nullable=True)
    status = db.Column(db.Enum(SessionStatus), nullable=False, default=SessionStatus.QUEUED)
    queued_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Float, nullable=True)
    log_output = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    passed_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    total_count = db.Column(db.Integer, default=0)
    screenshots = db.Column(db.Text, default="[]") 

    device = db.relationship("Device", back_populates="sessions")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "device_id": self.device_id,
            "device_udid": self.device.udid if self.device else None,
            "device_name": self.device.name if self.device else None,
            "test_name": self.test_name,
            "test_file": self.test_file,
            "app_path": self.app_path,
            "status": self.status.value,
            "queued_at": self.queued_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": self.duration_seconds,
            "log_output": self.log_output,
            "error_message": self.error_message,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "total_count": self.total_count,
            "screenshots": json.loads(self.screenshots or "[]"),
        }

    def __repr__(self):
        return f"<TestSession {self.session_id} [{self.status.value}]>"