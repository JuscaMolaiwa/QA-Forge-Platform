import subprocess
import socket
import time
from typing import Optional

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

_appium_processes: dict[int, subprocess.Popen] = {}


def _port_free(port: int) -> bool:
    for host in ("127.0.0.1", "::1"):
        try:
            family = socket.AF_INET6 if host == "::1" else socket.AF_INET
            with socket.socket(family, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex((host, port)) == 0:
                    return False
        except OSError:
            pass
    return True


def _wait_for_port(port: int, timeout: int = 30) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not _port_free(port):
            return True
        time.sleep(0.5)
    return False


def find_free_port(config: Config) -> Optional[int]:
    """Find the next available Appium port."""
    # When using a remote Appium (ngrok), return the base port as a token
    if config.APPIUM_HOST.startswith("http"):
        return config.APPIUM_BASE_PORT
    for offset in range(config.APPIUM_MAX_SESSIONS):
        port = config.APPIUM_BASE_PORT + offset
        if _port_free(port) and port not in _appium_processes:
            return port
    return None


def start_appium(config: Config, port: int) -> bool:
    """Start an Appium server — or skip if using a remote/ngrok URL."""
    # Remote Appium (ngrok or any http host) — nothing to start locally
    if config.APPIUM_HOST.startswith("http"):
        logger.info("Remote Appium at %s — skipping local start", config.APPIUM_URL)
        return True

    if port in _appium_processes:
        proc = _appium_processes[port]
        if proc.poll() is None:
            logger.info("Appium already running on port %d", port)
            return True
        del _appium_processes[port]

    import os
    log_path = f"/tmp/appium_{port}.log"
    try:
        log_file = open(log_path, "w")
        proc = subprocess.Popen(
            ["appium", "--port", str(port), "--address", config.APPIUM_HOST,
             "--relaxed-security", "--log-level", "info"],
            stdout=log_file,
            stderr=log_file,
            env={**os.environ, "PATH": "/opt/homebrew/bin:" + os.environ.get("PATH", "")},
        )
        _appium_processes[port] = proc
        logger.info("Started Appium on port %d (pid %d) — log: %s", port, proc.pid, log_path)

        if not _wait_for_port(port, timeout=30):
            log_file.flush()
            try:
                with open(log_path) as f:
                    tail = f.read()[-2000:]
                logger.error("Appium on port %d did not start. Output:\n%s", port, tail)
            except OSError:
                pass
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
    """Stop the Appium server on the given port (no-op for remote)."""
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
