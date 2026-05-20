"""
conftest.py — auto-screenshot plugin for the Appium Device Farm.

Injected automatically by the test executor alongside every test run.
Captures a screenshot after every test function and on failures,
then writes them to the backend DB via the REST API.
"""
import base64
import os
import json
import traceback

import pytest
import requests

# Farm API config (injected as env vars by the executor) 
FARM_API = os.environ.get("FARM_API_URL", "http://localhost:5000")
SESSION_ID = os.environ.get("FARM_SESSION_ID", "")
APPIUM_HOST = os.environ.get("APPIUM_HOST", "localhost")
APPIUM_PORT = os.environ.get("APPIUM_PORT", "4723")

_step_index = 0
_driver_ref = [None]


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
    if driver is None or not SESSION_ID:
        return
    try:
        png_b64 = driver.get_screenshot_as_base64()
        _step_index += 1
        requests.post(
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
    except Exception:
        pass  # never fail the test because of a screenshot error


# Hooks 

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if call.when == "call":          # only after the actual test body runs
        driver = _get_driver(item)
        passed = report.passed
        step_name = item.name
        _capture(driver, step_name, passed)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    """Also capture on setup failures (e.g. fixture errors)."""
    pass  # handled in makereport