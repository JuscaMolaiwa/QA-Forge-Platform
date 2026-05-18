"""
Sample Appium login test.
Run via the Device Farm UI — environment variables are injected automatically.
"""
import os
import pytest
from appium import webdriver
from appium.options import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy


@pytest.fixture(scope="module")
def driver():
    opts = AppiumOptions()
    opts.platform_name = os.environ.get("PLATFORM_NAME", "Android")
    opts.set_capability("appium:udid", os.environ.get("DEVICE_UDID", ""))
    opts.set_capability("appium:app", os.environ.get("APP_PATH", ""))
    opts.set_capability("appium:automationName", "UiAutomator2")
    opts.set_capability("appium:newCommandTimeout", 120)

    host = os.environ.get("APPIUM_HOST", "localhost")
    port = os.environ.get("APPIUM_PORT", "4723")
    drv = webdriver.Remote(f"http://{host}:{port}", options=opts)
    yield drv
    drv.quit()


def test_login_screen_loads(driver):
    """Verify the login screen is displayed on launch."""
    username_field = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "username_input")
    assert username_field.is_displayed(), "Username field should be visible"


def test_login_with_valid_credentials(driver):
    """Perform a login with valid credentials."""
    username = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "username_input")
    password = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "password_input")
    login_btn = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "login_button")

    username.clear()
    username.send_keys("testuser@example.com")
    password.clear()
    password.send_keys("SecureP@ss123")
    login_btn.click()

    # Assert navigation to home screen
    home = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "home_screen")
    assert home.is_displayed(), "Should navigate to home after successful login"


def test_login_with_invalid_credentials(driver):
    """Verify error message on bad credentials."""
    username = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "username_input")
    password = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "password_input")
    login_btn = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "login_button")

    username.clear()
    username.send_keys("wrong@example.com")
    password.clear()
    password.send_keys("wrongpassword")
    login_btn.click()

    error = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "error_message")
    assert error.is_displayed(), "Error message should appear for invalid login"
