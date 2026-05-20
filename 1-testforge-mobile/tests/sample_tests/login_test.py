"""
Appium login test targeting the Sauce Labs sample app (saucedemo APK).
Run via the Device Farm UI — environment variables are injected automatically.
"""
import os
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WAIT = 15
ERROR_TEXT = "Username and password do not match any user in this service."


@pytest.fixture(scope="module")
def driver():
    opts = UiAutomator2Options()

    # Core device config
    opts.platform_name = "Android"
    opts.automation_name = "UiAutomator2"

    # Device selection (only if provided)
    udid = os.getenv("DEVICE_UDID")
    if udid:
        opts.udid = udid

    # App config
    app_path = os.getenv("APP_PATH")
    if app_path:
        opts.app = app_path

    opts.app_package = "com.swaglabsmobileapp"
    opts.app_activity = "com.swaglabsmobileapp.SplashActivity"

    # Session behavior
    opts.new_command_timeout = 180
    opts.auto_grant_permissions = True

    # Docker/emulator timeout fixes
    opts.uiautomator2_server_launch_timeout = 60000
    opts.uiautomator2_server_install_timeout = 60000
    opts.adb_exec_timeout = 60000
    opts.android_device_ready_timeout = 60000

    # Appium server selection
    host = os.getenv("APPIUM_HOST", "localhost")
    port = os.getenv("APPIUM_PORT", "4723")

    if host.startswith("http"):
        appium_url = host
    else:
        appium_url = f"http://{host}:{port}"

    driver = webdriver.Remote(
        command_executor=appium_url,
        options=opts
    )

    yield driver
    driver.quit()


def wait_for(driver, accessibility_id: str):
    return WebDriverWait(driver, WAIT).until(
        EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
    )


def wait_for_text(driver, text: str):
    return WebDriverWait(driver, WAIT).until(
        EC.visibility_of_element_located((
            AppiumBy.XPATH, f'//*[@text="{text}"]'
        ))
    )


def _wait_for_login_screen(driver):
    wait_for(driver, "test-Username")
    wait_for(driver, "test-Password")
    wait_for(driver, "test-LOGIN")


def _do_login(driver, username: str, password: str) -> None:
    _wait_for_login_screen(driver)
    username_field = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Username")
    username_field.clear()
    username_field.send_keys(username)
    password_field = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Password")
    password_field.clear()
    password_field.send_keys(password)
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-LOGIN").click()


def test_login_screen_loads(driver):
    """Verify the login screen elements are visible on launch."""
    _wait_for_login_screen(driver)
    assert driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Username").is_displayed()
    assert driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Password").is_displayed()
    assert driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-LOGIN").is_displayed()


def test_login_with_valid_credentials(driver):
    """Log in with standard_user and confirm navigation to the product catalogue."""
    _do_login(driver, "standard_user", "secret_sauce")

    catalogue = wait_for(driver, "test-PRODUCTS")
    assert catalogue.is_displayed(), "Should land on the Products screen after login"

    wait_for(driver, "test-Menu").click()
    wait_for(driver, "test-LOGOUT").click()
    _wait_for_login_screen(driver)


def test_login_with_invalid_credentials(driver):
    """Verify error message appears for wrong credentials."""
    _do_login(driver, "wrong_user", "wrong_pass")

    error = wait_for_text(driver, ERROR_TEXT)
    assert error.is_displayed(), f"Expected error: '{ERROR_TEXT}'"