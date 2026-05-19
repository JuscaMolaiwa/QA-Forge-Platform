from datetime import datetime, timezone
from extensions import db


class TestScript(db.Model):
    __tablename__ = "test_scripts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    filename = db.Column(db.String(256), nullable=False, unique=True, index=True)
    description = db.Column(db.String(512), nullable=True)
    content = db.Column(db.Text, nullable=False)
    platform = db.Column(db.String(16), nullable=False, default="android")
    tags = db.Column(db.String(256), nullable=True)   # comma-separated
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self, include_content=True):
        d = {
            "id": self.id,
            "name": self.name,
            "filename": self.filename,
            "description": self.description,
            "platform": self.platform,
            "tags": [t.strip() for t in self.tags.split(",")] if self.tags else [],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_content:
            d["content"] = self.content
        return d

    def __repr__(self):
        return f"<TestScript {self.filename}>"
