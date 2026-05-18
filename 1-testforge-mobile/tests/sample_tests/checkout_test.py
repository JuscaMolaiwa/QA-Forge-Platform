"""
Sample Appium checkout flow test.
Demonstrates multi-step UI interaction with assertions.
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
    opts.set_capability("appium:newCommandTimeout", 180)

    host = os.environ.get("APPIUM_HOST", "localhost")
    port = os.environ.get("APPIUM_PORT", "4723")
    drv = webdriver.Remote(f"http://{host}:{port}", options=opts)
    yield drv
    drv.quit()


def test_product_list_loads(driver):
    """Verify product listing page loads at least one item."""
    items = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "product_item")
    assert len(items) > 0, "Product list should not be empty"


def test_add_to_cart(driver):
    """Add first product to cart and verify cart count updates."""
    first_item = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "product_item")[0]
    first_item.find_element(AppiumBy.ACCESSIBILITY_ID, "add_to_cart_btn").click()

    cart_badge = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "cart_badge")
    assert cart_badge.text == "1", "Cart badge should show 1 item"


def test_proceed_to_checkout(driver):
    """Open cart and proceed to checkout screen."""
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "cart_icon").click()
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "checkout_btn").click()

    checkout_title = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "checkout_title")
    assert checkout_title.is_displayed(), "Checkout screen should be visible"


def test_order_summary_shows_correct_total(driver):
    """Assert order summary contains a non-zero total."""
    total_element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "order_total")
    total_text = total_element.text  # e.g. "$19.99"
    assert total_text.startswith("$"), "Total should be a currency value"
    assert float(total_text.replace("$", "").replace(",", "")) > 0, "Total should be positive"
