import enum
from datetime import datetime, timezone
from extensions import db


class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    udid = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)
    platform = db.Column(db.String(16), nullable=False)   # android | ios
    platform_version = db.Column(db.String(16), nullable=True)
    model = db.Column(db.String(64), nullable=True)
    status = db.Column(db.Enum(DeviceStatus), nullable=False, default=DeviceStatus.OFFLINE)
    appium_port = db.Column(db.Integer, nullable=True)
    is_cloud = db.Column(db.Boolean, default=False)
    cloud_provider = db.Column(db.String(32), nullable=True)
    last_seen = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    sessions = db.relationship("TestSession", back_populates="device", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "udid": self.udid,
            "name": self.name,
            "platform": self.platform,
            "platform_version": self.platform_version,
            "model": self.model,
            "status": self.status.value,
            "appium_port": self.appium_port,
            "is_cloud": self.is_cloud,
            "cloud_provider": self.cloud_provider,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<Device {self.udid} [{self.status.value}]>"
