"""
Appium login test targeting the Sauce Labs sample app (saucedemo APK).
Run via the Device Farm UI — environment variables are injected automatically.
"""
import os
import pytest
from appium import webdriver
from appium.options.android.uiautomator2.base import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


WAIT = 15
ERROR_TEXT = "Username and password do not match any user in this service."


@pytest.fixture(scope="module")
def driver():
    opts = UiAutomator2Options()
    opts.platform_name = "Android"
    opts.set_capability("appium:udid", os.environ.get("DEVICE_UDID", ""))
    opts.set_capability("appium:app", os.environ.get("APP_PATH", ""))
    opts.set_capability("appium:appPackage", "com.swaglabsmobileapp")
    opts.set_capability("appium:appActivity", "com.swaglabsmobileapp.SplashActivity")
    opts.set_capability("appium:automationName", "UiAutomator2")
    opts.set_capability("appium:newCommandTimeout", 120)
    opts.set_capability("appium:autoGrantPermissions", True)

    host = os.environ.get("APPIUM_HOST", "localhost")
    port = os.environ.get("APPIUM_PORT", "4723")

    if host.endswith(".ngrok-free.app") or host.endswith(".ngrok.io"):
        appium_url = f"https://{host}"
    else:
        appium_url = f"http://{host}:{port}"

    drv = webdriver.Remote(appium_url, options=opts)

    yield drv
    drv.quit()


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