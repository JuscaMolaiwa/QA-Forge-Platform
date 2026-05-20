from datetime import datetime, timezone
from typing import List, Optional

from extensions import db
from models import Device, DeviceStatus
from config import Config
from utils.adb_helper import list_devices, is_device_online
from utils.logger import get_logger

logger = get_logger(__name__)


class DeviceManager:
    """Discovers, registers, and tracks connected devices."""

    def __init__(self, config: Config):
        self.config = config

    def sync_adb_devices(self) -> List[Device]:
        """Scan ADB for connected devices and sync to DB."""
        adb_devices = list_devices(self.config.ADB_PATH)
        synced = []

        for info in adb_devices:
            device = Device.query.filter_by(udid=info["udid"]).first()
            if device is None:
                device = Device(
                    udid=info["udid"],
                    name=info.get("name", info["udid"]),
                    platform=info.get("platform", "android"),
                    platform_version=info.get("platform_version"),
                    model=info.get("model"),
                    is_cloud=False,
                )
                db.session.add(device)
                logger.info("Registered new device: %s", info["udid"])

            device.status = DeviceStatus.ONLINE
            device.last_seen = datetime.now(timezone.utc)
            db.session.commit()
            synced.append(device)

        # Mark devices not seen in this scan as offline
        known_udids = {d["udid"] for d in adb_devices}
        for device in Device.query.filter(
            Device.is_cloud.is_(False),
            Device.status == DeviceStatus.ONLINE,
        ).all():
            if device.udid not in known_udids:
                device.status = DeviceStatus.OFFLINE
                db.session.commit()
                logger.info("Device went offline: %s", device.udid)

        return synced

    def get_available_device(self, platform: Optional[str] = None) -> Optional[Device]:
        """Return the first available (online, not busy) device."""
        query = Device.query.filter_by(status=DeviceStatus.ONLINE)
        if platform:
            query = query.filter_by(platform=platform.lower())
        return query.first()

    def mark_busy(self, device: Device, appium_port: int) -> None:
        device.status = DeviceStatus.BUSY
        device.appium_port = appium_port
        db.session.commit()

    def mark_available(self, device: Device) -> None:
        device.status = DeviceStatus.ONLINE
        device.appium_port = None
        db.session.commit()

    def mark_error(self, device: Device) -> None:
        device.status = DeviceStatus.ERROR
        device.appium_port = None
        db.session.commit()

    # def register_device(self, data: dict) -> Device:
    #     """Manually register a device (e.g. cloud or remote)."""
    #     device = Device.query.filter_by(udid=data["udid"]).first()
    #     if device is None:
    #         device = Device(
    #             udid=data["udid"],
    #             name=data["name"],
    #             platform=data["platform"].lower(),
    #             platform_version=data.get("platform_version"),
    #             model=data.get("model"),
    #             is_cloud=data.get("is_cloud", False),
    #             cloud_provider=data.get("cloud_provider"),
    #         )
    #         db.session.add(device)
    #     else:
    #         device.name = data["name"]
    #         device.platform = data["platform"].lower()

    #     device.status = DeviceStatus.ONLINE
    #     device.last_seen = datetime.now(timezone.utc)
    #     db.session.commit()
    #     return device

    def register_device(self, data: dict) -> Device:
        """Manually register a device (e.g. cloud or remote)."""
        existing = Device.query.filter_by(udid=data["udid"]).first()
        if existing:
            raise ValueError(
                f"Device with UDID '{data['udid']}' is already registered."
            )

        device = Device(
            udid=data["udid"],
            name=data["name"],
            platform=data["platform"].lower(),
            platform_version=data.get("platform_version"),
            model=data.get("model"),
            is_cloud=data.get("is_cloud", False),
            cloud_provider=data.get("cloud_provider"),
        )
        db.session.add(device)
        device.status = DeviceStatus.ONLINE
        device.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        return device

    def all_devices(self) -> List[Device]:
        return Device.query.order_by(Device.created_at.desc()).all()

    def get_by_id(self, device_id: int) -> Optional[Device]:
        return Device.query.get(device_id)

    def delete_device(self, device: Device) -> None:
        db.session.delete(device)
        db.session.commit()
