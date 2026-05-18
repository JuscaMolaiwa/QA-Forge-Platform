from flask import Blueprint, jsonify, request, current_app
from utils.validators import validate_device_payload

devices_bp = Blueprint("devices", __name__, url_prefix="/api/devices")


def _dm():
    return current_app.device_manager


@devices_bp.get("/")
def list_devices():
    devices = _dm().all_devices()
    return jsonify([d.to_dict() for d in devices])


@devices_bp.post("/")
def register_device():
    data = request.get_json(silent=True) or {}
    ok, msg = validate_device_payload(data)
    if not ok:
        return jsonify({"error": msg}), 400
    device = _dm().register_device(data)
    return jsonify(device.to_dict()), 201


@devices_bp.get("/<int:device_id>")
def get_device(device_id):
    device = _dm().get_by_id(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    return jsonify(device.to_dict())


@devices_bp.delete("/<int:device_id>")
def delete_device(device_id):
    device = _dm().get_by_id(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    _dm().delete_device(device)
    return jsonify({"message": "Device deleted"})


@devices_bp.post("/sync")
def sync_devices():
    """Trigger an ADB scan to discover and sync connected devices."""
    synced = _dm().sync_adb_devices()
    return jsonify({"synced": len(synced), "devices": [d.to_dict() for d in synced]})
