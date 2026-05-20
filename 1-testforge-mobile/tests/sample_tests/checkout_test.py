"""
Appium checkout flow test targeting the Sauce Labs sample app (saucedemo APK).
Run via the Device Farm UI — environment variables are injected automatically.
"""
import os
import pytest
from appium import webdriver
from appium.options.android.uiautomator2.base import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy


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

    # Log in once for the entire module
    drv.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Username").send_keys("standard_user")
    drv.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Password").send_keys("secret_sauce")
    drv.find_element(AppiumBy.ACCESSIBILITY_ID, "test-LOGIN").click()

    yield drv
    drv.quit()


def test_product_list_loads(driver):
    """Verify the Products screen loads with at least one item."""
    catalogue = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-PRODUCTS")
    assert catalogue.is_displayed(), "Products header should be visible"

    items = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "test-Item title")
    assert len(items) > 0, "Product list should contain at least one item"


def test_add_to_cart(driver):
    """Add the first product to the cart and verify the cart badge shows 1."""
    add_buttons = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "test-ADD TO CART")
    assert len(add_buttons) > 0, "At least one Add to Cart button should be present"
    add_buttons[0].click()

    cart_badge = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Cart")
    badge_text = cart_badge.find_element(AppiumBy.XPATH, ".//*[@content-desc='test-Cart item quantity']").text
    assert badge_text == "1", f"Cart badge should read '1', got '{badge_text}'"


def test_proceed_to_checkout(driver):
    """Open the cart and proceed to the checkout information screen."""
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Cart").click()
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-CHECKOUT").click()

    assert driver.find_element(
        AppiumBy.ACCESSIBILITY_ID, "test-CHECKOUT: INFORMATION"
    ).is_displayed(), "Checkout Information screen should be visible"

    # Fill in required shipping fields
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-First Name").send_keys("Test")
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Last Name").send_keys("User")
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Zip/Postal Code").send_keys("12345")
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-CONTINUE").click()


def test_order_summary_shows_correct_total(driver):
    """Assert the order summary screen shows a positive currency total."""
    assert driver.find_element(
        AppiumBy.ACCESSIBILITY_ID, "test-CHECKOUT: OVERVIEW"
    ).is_displayed(), "Checkout Overview screen should be visible"

    total_element = driver.find_element(AppiumBy.XPATH, '//*[@content-desc="test-Price total"]')
    total_text = total_element.text  # e.g. "Item total: $9.99"

    # Extract the dollar amount from the label
    amount_str = total_text.split("$")[-1].replace(",", "").strip()
    assert float(amount_str) > 0, f"Order total should be positive, got: '{total_text}'"