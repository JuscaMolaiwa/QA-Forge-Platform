import atexit
import socket
import subprocess
import threading
import time
from typing import Optional

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

_appium_processes: dict[int, Optional[subprocess.Popen]] = {}
_lock = threading.Lock()


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0


def _wait_for_port(port: int, timeout: int = 20) -> bool:
    deadline = time.time() + timeout
    interval = 0.1
    while time.time() < deadline:
        if not _port_free(port):
            return True
        time.sleep(interval)
        interval = min(interval * 1.5, 0.5)
    return False


def _cleanup_all() -> None:
    for port in list(_appium_processes):
        stop_appium(port)


atexit.register(_cleanup_all)


def find_free_port(config: Config) -> Optional[int]:
    """Find and atomically reserve the next available Appium port."""
    with _lock:
        for offset in range(config.APPIUM_MAX_SESSIONS):
            port = config.APPIUM_BASE_PORT + offset
            if _port_free(port) and port not in _appium_processes:
                _appium_processes[port] = None  # reserve slot
                return port
    return None


def start_appium(config: Config, port: int) -> bool:
    """Start an Appium server on the given port and wait for it to be ready."""
    with _lock:
        existing = _appium_processes.get(port, "absent")

        if existing == "absent":
            # Port was not reserved via find_free_port; reserve it now if free.
            if not _port_free(port):
                logger.error("Port %d is already in use by an untracked process", port)
                return False
            _appium_processes[port] = None

        elif existing is not None:
            # A live Popen handle exists.
            if existing.poll() is None:
                logger.info("Appium already running on port %d", port)
                return True
            # Process died; clear the stale entry and re-launch below.
            del _appium_processes[port]
            _appium_processes[port] = None

        # At this point _appium_processes[port] is None (reserved, not started).

    try:
        proc = subprocess.Popen(
            [
                "appium",
                "--port", str(port),
                "--address", config.APPIUM_HOST,
                "--relaxed-security",
                "--log-level", "warn",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        with _lock:
            _appium_processes[port] = proc

        logger.info("Started Appium on port %d (pid %d)", port, proc.pid)

        if not _wait_for_port(port, timeout=20):
            logger.error("Appium on port %d did not start in time", port)
            proc.kill()
            with _lock:
                _appium_processes.pop(port, None)
            return False

        return True

    except FileNotFoundError:
        logger.error("'appium' not found — install via: npm i -g appium")
        with _lock:
            _appium_processes.pop(port, None)
        return False

    except Exception as exc:
        logger.exception("Failed to start Appium on port %d: %s", port, exc)
        with _lock:
            _appium_processes.pop(port, None)
        return False


def stop_appium(port: int) -> None:
    """Stop the Appium server running on the given port."""
    with _lock:
        if port not in _appium_processes:
            logger.debug("No tracked Appium process on port %d", port)
            return
        proc = _appium_processes.pop(port)

    if proc is None:
        logger.debug("Port %d was reserved but never started", port)
        return

    if proc.poll() is not None:
        logger.debug("Appium on port %d had already exited", port)
        return

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

    logger.info("Stopped Appium on port %d", port)


def is_appium_running(port: int) -> bool:
    """Return True only if the process is tracked, alive, and listening on the port."""
    with _lock:
        proc = _appium_processes.get(port)

    if proc is None:
        return False

    return proc.poll() is None and not _port_free(port)