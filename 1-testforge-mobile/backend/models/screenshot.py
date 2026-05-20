from datetime import datetime, timezone
from extensions import db


class Screenshot(db.Model):
    __tablename__ = "screenshots"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), db.ForeignKey("test_sessions.session_id"),
                           nullable=False, index=True)
    step_name = db.Column(db.String(256), nullable=False)
    step_index = db.Column(db.Integer, nullable=False, default=0)
    image_b64 = db.Column(db.Text, nullable=False)   # base64 PNG
    captured_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    passed = db.Column(db.Boolean, nullable=True)     # True/False/None = unknown

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "step_name": self.step_name,
            "step_index": self.step_index,
            "image_b64": self.image_b64,
            "captured_at": self.captured_at.isoformat(),
            "passed": self.passed,
        }

    def __repr__(self):
        return f"<Screenshot {self.session_id} step={self.step_index}>"