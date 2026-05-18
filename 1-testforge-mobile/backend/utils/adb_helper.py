import subprocess
import re
from typing import List, Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def _run(args: List[str], timeout: int = 10) -> tuple[int, str, str]:
    """Run an adb command, return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except FileNotFoundError:
        return 1, "", "adb not found — ensure Android SDK platform-tools are on PATH"


def list_devices(adb_path: str = "adb") -> List[Dict]:
    """Return a list of connected ADB devices with basic info."""
    code, out, err = _run([adb_path, "devices", "-l"])
    if code != 0:
        logger.error("adb devices failed: %s", err)
        return []

    devices = []
    for line in out.splitlines()[1:]:  # skip header line
        line = line.strip()
        if not line or "offline" in line or "unauthorized" in line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        udid = parts[0]
        props = _parse_device_props(parts[2:])
        info = _fetch_device_info(adb_path, udid)
        devices.append({
            "udid": udid,
            "name": info.get("ro.product.model", udid),
            "platform": "android",
            "platform_version": info.get("ro.build.version.release", "unknown"),
            "model": info.get("ro.product.model", "unknown"),
            **props,
        })
    return devices


def _parse_device_props(tokens: List[str]) -> Dict:
    result = {}
    for token in tokens:
        if ":" in token:
            k, v = token.split(":", 1)
            result[k] = v
    return result


def _fetch_device_info(adb_path: str, udid: str) -> Dict:
    """Fetch device properties via adb shell getprop."""
    keys = ["ro.product.model", "ro.build.version.release", "ro.product.manufacturer"]
    info = {}
    for key in keys:
        code, out, _ = _run([adb_path, "-s", udid, "shell", "getprop", key])
        if code == 0 and out:
            info[key] = out
    return info


def is_device_online(adb_path: str, udid: str) -> bool:
    """Return True if the device responds to adb shell echo."""
    code, out, _ = _run([adb_path, "-s", udid, "shell", "echo", "ping"])
    return code == 0 and out.strip() == "ping"


def connect_tcp(adb_path: str, host: str, port: int = 5555) -> bool:
    """Connect to a remote device over TCP/IP."""
    code, out, err = _run([adb_path, "connect", f"{host}:{port}"])
    if code == 0 and "connected" in out.lower():
        logger.info("ADB TCP connect OK: %s:%s", host, port)
        return True
    logger.warning("ADB TCP connect failed: %s", err or out)
    return False


def get_installed_packages(adb_path: str, udid: str) -> List[str]:
    """Return list of installed package names on device."""
    code, out, _ = _run([adb_path, "-s", udid, "shell", "pm", "list", "packages"], timeout=20)
    if code != 0:
        return []
    packages = []
    for line in out.splitlines():
        match = re.match(r"package:(.+)", line.strip())
        if match:
            packages.append(match.group(1))
    return packages
