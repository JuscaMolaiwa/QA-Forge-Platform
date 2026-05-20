import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from extensions import db, socketio
from models import TestSession, SessionStatus, Device
from services.appium_service import find_free_port, start_appium, stop_appium
from services.device_manager import DeviceManager
from services.queue_manager import QueueManager
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class TestExecutor:
    """Pulls sessions from the queue and runs them against available devices."""

    def __init__(self, config: Config, device_manager: DeviceManager, queue: QueueManager):
        self.config = config
        self.device_manager = device_manager
        self.queue = queue
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._app_context = None

    def start(self, app) -> None:
        self._app_context = app.app_context
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="TestExecutor")
        self._thread.start()
        logger.info("TestExecutor started")

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("TestExecutor stopped")

    def _loop(self) -> None:
        while self._running:
            session_id = self.queue.dequeue()
            if session_id:
                with self._app_context():
                    db.session.expire_all()  # force fresh read each cycle
                    self._execute(session_id)
            else:
                time.sleep(1)

    def _emit(self, event: str, data: dict) -> None:
        try:
            socketio.emit(event, data)
        except Exception as exc:
            logger.debug("SocketIO emit failed: %s", exc)

    def _execute(self, session_id: str) -> None:
        db.session.expire_all() 
        session: Optional[TestSession] = TestSession.query.filter_by(
            session_id=session_id
        ).first()
        if not session:
            logger.warning("Session not found: %s", session_id)
            return

        # Pick a device
        device = self.device_manager.get_available_device()
        if not device:
            logger.info("No device available for %s — re-queuing", session_id)
            self.queue.enqueue(session_id)
            time.sleep(3)
            return

        # Allocate Appium port
        port = find_free_port(self.config)
        if port is None:
            logger.error("No free Appium port for %s", session_id)
            self._fail(session, "No free Appium port available")
            return

        # Start Appium
        if not start_appium(self.config, port):
            self._fail(session, "Failed to start Appium server")
            return

        self.device_manager.mark_busy(device, port)
        session.device_id = device.id
        session.status = SessionStatus.RUNNING
        session.started_at = datetime.now(timezone.utc)
        db.session.commit()

        self._emit("session_update", session.to_dict())
        logger.info("Running %s on device %s port %d", session_id, device.udid, port)

        try:
            log_output, passed, failed, total = self._run_test(session, device, port)
            session.log_output = log_output
            session.passed_count = passed
            session.failed_count = failed
            session.total_count = total
            session.status = SessionStatus.PASSED if failed == 0 else SessionStatus.FAILED
        except Exception as exc:
            logger.exception("Execution error for %s: %s", session_id, exc)
            session.error_message = str(exc)
            session.status = SessionStatus.ERROR
        finally:
            session.finished_at = datetime.now(timezone.utc)
            if session.started_at:
                delta = session.finished_at - session.started_at.replace(
                    tzinfo=timezone.utc
                ) if session.started_at.tzinfo is None else session.finished_at - session.started_at
                session.duration_seconds = delta.total_seconds()
            db.session.commit()
            stop_appium(port)
            self.device_manager.mark_available(device)
            self._emit("session_update", session.to_dict())
            logger.info("Session %s finished: %s", session_id, session.status.value)

    def _run_test(
        self, session: TestSession, device: Device, port: int
    ) -> tuple[str, int, int, int]:
        """Write the test to a temp file and run it via pytest."""
        tmp_path = None
        try:
            if session.test_content:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".py",
                    prefix="test_",
                    delete=False,
                    dir=tempfile.gettempdir(),
                ) as f:
                    f.write(session.test_content)
                    tmp_path = f.name
                test_path = tmp_path
            else:
                test_path = session.test_file

            env = os.environ.copy()
            env.update({
                "APPIUM_HOST": self.config.APPIUM_URL,  # full URL - handles ngrok & local
                "APPIUM_PORT": str(port),
                "DEVICE_UDID": device.udid,
                "PLATFORM_NAME": device.platform,
                "PLATFORM_VERSION": device.platform_version or "",
                "APP_PATH": session.app_path or "",
            })

            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short", "--no-header"],
                capture_output=True,
                text=True,
                timeout=self.config.SESSION_TIMEOUT_SECONDS,
                env=env,
            )
            log_output = result.stdout + ("\n" + result.stderr if result.stderr else "")
            passed, failed, total = _parse_pytest_summary(log_output)
            return log_output, passed, failed, total

        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    def _fail(self, session: TestSession, message: str) -> None:
        session.status = SessionStatus.ERROR
        session.error_message = message
        session.finished_at = datetime.now(timezone.utc)
        db.session.commit()
        self._emit("session_update", session.to_dict())


def _parse_pytest_summary(log: str) -> tuple[int, int, int]:
    """Extract passed/failed/total from pytest summary line."""
    match = re.search(
        r"(\d+) passed(?:,\s*(\d+) failed)?|(\d+) failed(?:,\s*(\d+) passed)?",
        log,
    )
    if not match:
        return 0, 0, 0
    groups = match.groups(default="0")
    if match.group(1):
        passed, failed = int(groups[0]), int(groups[1])
    else:
        failed, passed = int(groups[2]), int(groups[3])
    return passed, failed, passed + failed


def create_session(test_name: str, test_content: str = "", test_file: str = "",
                   app_path: str = "") -> TestSession:
    session = TestSession(
        session_id=str(uuid.uuid4()),
        test_name=test_name,
        test_content=test_content,
        test_file=test_file,
        app_path=app_path,
        status=SessionStatus.QUEUED,
    )
    db.session.add(session)
    db.session.commit()
    return session
