"""
conftest.py — auto-screenshot plugin for the Appium Device Farm.

Injected automatically by the test executor alongside every test run.
Captures a screenshot after every test function and POSTs to the backend DB.
"""

import os
import requests
import pytest

# Farm API config (injected as env vars by the executor)
FARM_API = (
    os.environ.get("FARM_API_URL")
    or os.environ.get("RENDER_EXTERNAL_URL")
    or "http://localhost:5000"
)
SESSION_ID = os.environ.get("FARM_SESSION_ID", "")

_step_index = 0


def _get_driver(item):
    """Pull the appium driver from the test's fixtures."""
    for name in ("driver", "appium_driver", "d"):
        fix = item.funcargs.get(name)
        if fix is not None:
            return fix
    return None


def _capture(driver, step_name: str, passed: bool):
    """Take a screenshot and POST it to the farm API."""
    global _step_index

    print(
        f"\n[conftest] _capture called: step={step_name} driver={driver is not None} session_id='{SESSION_ID}' api={FARM_API}"
    )

    if driver is None:
        print("[conftest] skipping — no driver found in fixtures")
        return
    if not SESSION_ID:
        print("[conftest] skipping — FARM_SESSION_ID env var is empty")
        return

    try:
        png_b64 = driver.get_screenshot_as_base64()
        _step_index += 1
        resp = requests.post(
            f"{FARM_API}/api/reports/screenshots",
            json={
                "session_id": SESSION_ID,
                "step_name": step_name,
                "step_index": _step_index,
                "image_b64": png_b64,
                "passed": passed,
            },
            timeout=10,
        )
        print(
            f"[conftest] screenshot posted — status={resp.status_code} step={_step_index}"
        )
    except Exception as exc:
        print(f"[conftest] screenshot failed — {type(exc).__name__}: {exc}")


# Hooks
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if call.when == "call":
        driver = _get_driver(item)
        _capture(driver, item.name, report.passed)
