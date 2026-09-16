"""
Tests for Phase 4: Privacy Protection and Safety Review
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from phase4.privacy_filter import (
    mask_pii_in_text,
    privacy_filter_review,
    privacy_filter_reviews,
    validate_no_pii_remaining,
)


def test_mask_email():
    text, counts = mask_pii_in_text("Please contact me at user@example.com about this issue")
    assert "user@example.com" not in text
    assert "[EMAIL]" in text
    assert counts["email"] == 1
    print("  PASS: test_mask_email")


def test_mask_phone():
    text, counts = mask_pii_in_text("My phone is +1 555 123 4567 please call me")
    assert "555 123 4567" not in text
    assert "[PHONE]" in text
    assert counts["phone"] == 1
    print("  PASS: test_mask_phone")


def test_mask_username():
    text, counts = mask_pii_in_text("My handle is @testuser and support ignored me")
    assert "@testuser" not in text
    assert "[USERNAME]" in text
    assert counts["username"] == 1
    print("  PASS: test_mask_username")


def test_mask_ip_address():
    text, counts = mask_pii_in_text("Login failed from IP 192.168.1.25 yesterday")
    assert "192.168.1.25" not in text
    assert "[IP_ADDRESS]" in text
    assert counts["ip_address"] == 1
    print("  PASS: test_mask_ip_address")


def test_mask_account_id():
    text, counts = mask_pii_in_text("My account id ABCD12345 is locked after KYC")
    assert "ABCD12345" not in text
    assert "[ACCOUNT_ID]" in text
    assert counts["account_id"] == 1
    print("  PASS: test_mask_account_id")


def test_mask_reference_id():
    text, counts = mask_pii_in_text("Ticket number TCKT123456 has no update")
    assert "TCKT123456" not in text
    assert "[REFERENCE_ID]" in text
    assert counts["order_id"] == 1
    print("  PASS: test_mask_reference_id")


def test_mask_device_id():
    text, counts = mask_pii_in_text("Device id ZXCVB123456 crashes every time")
    assert "ZXCVB123456" not in text
    assert "[DEVICE_ID]" in text
    assert counts["device_id"] == 1
    print("  PASS: test_mask_device_id")


def test_privacy_filter_review_flags_pii():
    review = {
        "review_id": "test-1",
        "review_text": "My email user@example.com is linked to account id ABCD12345",
        "review_title": "Contact @testuser",
    }
    safe_review, findings = privacy_filter_review(review)
    assert safe_review["privacy_checked"] is True
    assert safe_review["pii_detected"] is True
    assert "email" in safe_review["pii_types_detected"]
    assert "account_id" in safe_review["pii_types_detected"]
    assert "username" in safe_review["pii_types_detected"]
    assert "user@example.com" not in safe_review["review_text"]
    print("  PASS: test_privacy_filter_review_flags_pii")


def test_privacy_filter_reviews_report():
    reviews = [
        {"review_id": "r1", "review_text": "This app works well with no private data", "review_title": "Good"},
        {"review_id": "r2", "review_text": "Email me at user@example.com for details", "review_title": "Bad"},
    ]
    safe_reviews, report = privacy_filter_reviews(reviews)
    assert len(safe_reviews) == 2
    assert report["input_count"] == 2
    assert report["reviews_with_pii"] == 1
    assert report["pii_detection_counts"]["email"] == 1
    print("  PASS: test_privacy_filter_reviews_report")


def test_validate_no_pii_remaining():
    reviews = [
        {"review_id": "r1", "review_text": "Email [EMAIL] was masked", "review_title": "Safe"},
        {"review_id": "r2", "review_text": "Still has user@example.com", "review_title": "Unsafe"},
    ]
    remaining = validate_no_pii_remaining(reviews)
    assert len(remaining) == 1
    assert remaining[0]["review_id"] == "r2"
    print("  PASS: test_validate_no_pii_remaining")


def run_all_tests():
    print("=" * 50)
    print("Phase 4 Privacy Tests")
    print("=" * 50)

    tests = [
        test_mask_email,
        test_mask_phone,
        test_mask_username,
        test_mask_ip_address,
        test_mask_account_id,
        test_mask_reference_id,
        test_mask_device_id,
        test_privacy_filter_review_flags_pii,
        test_privacy_filter_reviews_report,
        test_validate_no_pii_remaining,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {test.__name__} - {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {test.__name__} - {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)} tests")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
