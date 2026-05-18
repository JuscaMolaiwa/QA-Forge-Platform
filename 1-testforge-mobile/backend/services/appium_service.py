import subprocess
import socket
import time
from typing import Optional

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

_appium_processes: dict[int, subprocess.Popen] = {}


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0


def _wait_for_port(port: int, timeout: int = 20) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not _port_free(port):
            return True
        time.sleep(0.5)
    return False


def find_free_port(config: Config) -> Optional[int]:
    """Find the next available Appium port."""
    for offset in range(config.APPIUM_MAX_SESSIONS):
        port = config.APPIUM_BASE_PORT + offset
        if _port_free(port) and port not in _appium_processes:
            return port
    return None


def start_appium(config: Config, port: int) -> bool:
    """Start an Appium server on the given port and wait for it to be ready."""
    if port in _appium_processes:
        proc = _appium_processes[port]
        if proc.poll() is None:
            logger.info("Appium already running on port %d", port)
            return True
        del _appium_processes[port]

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
        _appium_processes[port] = proc
        logger.info("Started Appium on port %d (pid %d)", port, proc.pid)

        if not _wait_for_port(port, timeout=20):
            logger.error("Appium on port %d did not start in time", port)
            proc.kill()
            del _appium_processes[port]
            return False

        return True
    except FileNotFoundError:
        logger.error("'appium' not found — install via: npm i -g appium")
        return False
    except Exception as exc:
        logger.exception("Failed to start Appium on port %d: %s", port, exc)
        return False


def stop_appium(port: int) -> None:
    """Stop the Appium server running on the given port."""
    proc = _appium_processes.pop(port, None)
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        logger.info("Stopped Appium on port %d", port)


def is_appium_running(port: int) -> bool:
    if port not in _appium_processes:
        return False
    return _appium_processes[port].poll() is None
