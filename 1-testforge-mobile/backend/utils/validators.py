from typing import Tuple


def validate_test_payload(data: dict) -> Tuple[bool, str]:
    """Validate the payload for submitting a test session."""
    if not data:
        return False, "Request body is required"

    test_name = data.get("test_name", "").strip()
    if not test_name:
        return False, "'test_name' is required"
    if len(test_name) > 256:
        return False, "'test_name' must be 256 characters or fewer"

    has_content = bool(data.get("test_content", "").strip())
    has_file = bool(data.get("test_file", "").strip())
    if not has_content and not has_file:
        return False, "Either 'test_content' or 'test_file' is required"

    platform = data.get("platform", "").lower()
    if platform and platform not in ("android", "ios"):
        return False, "'platform' must be 'android' or 'ios'"

    return True, ""


def validate_device_payload(data: dict) -> Tuple[bool, str]:
    """Validate payload for manually registering a device."""
    if not data:
        return False, "Request body is required"

    for field in ("udid", "name", "platform"):
        if not data.get(field, "").strip():
            return False, f"'{field}' is required"

    if data["platform"].lower() not in ("android", "ios"):
        return False, "'platform' must be 'android' or 'ios'"

    return True, ""
