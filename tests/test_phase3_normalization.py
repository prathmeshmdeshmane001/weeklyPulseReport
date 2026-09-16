"""
Tests for Phase 3: Data Normalization and Cleanup
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from phase3.normalize_reviews import (
    contains_emoji,
    count_words,
    is_english_text,
    normalize_text,
    normalize_date,
    normalize_rating,
    get_rating_label,
    normalize_platform,
    normalize_integer,
    normalize_review,
    normalize_reviews,
    remove_duplicate_reviews,
)


def test_normalize_text():
    assert normalize_text("  hello   world  ") == "hello world"
    assert normalize_text(None) == ""
    print("  PASS: test_normalize_text")


def test_normalize_date():
    assert normalize_date("2026-05-14") == "2026-05-14"
    assert normalize_date("05/14/2026") == "2026-05-14"
    assert normalize_date("May 14, 2026") == "2026-05-14"
    assert normalize_date("bad-date") is None
    print("  PASS: test_normalize_date")


def test_normalize_rating():
    assert normalize_rating("5") == 5
    assert normalize_rating("4.0") == 4
    assert normalize_rating("0") is None
    assert normalize_rating("6") is None
    assert normalize_rating("bad") is None
    print("  PASS: test_normalize_rating")


def test_rating_label():
    assert get_rating_label(1) == "negative"
    assert get_rating_label(2) == "negative"
    assert get_rating_label(3) == "neutral"
    assert get_rating_label(4) == "positive"
    assert get_rating_label(5) == "positive"
    print("  PASS: test_rating_label")


def test_normalize_platform():
    assert normalize_platform("App Store") == "app_store"
    assert normalize_platform("ios") == "app_store"
    assert normalize_platform("Play Store") == "play_store"
    assert normalize_platform("Android") == "play_store"
    print("  PASS: test_normalize_platform")


def test_normalize_integer():
    assert normalize_integer("10") == 10
    assert normalize_integer("4.0") == 4
    assert normalize_integer("") == 0
    assert normalize_integer("bad") == 0
    print("  PASS: test_normalize_integer")


def test_quality_helpers():
    assert count_words("This review has six useful words") == 6
    assert contains_emoji("Great app 😊") is True
    assert contains_emoji("Great app without emoji") is False
    assert is_english_text("This is a clear English review without emoji") is True
    assert is_english_text("यह हिंदी समीक्षा है") is False
    print("  PASS: test_quality_helpers")


def test_normalize_review_standard_record():
    record = {
        "review_text": "  This is a great app for daily payments  ",
        "review_title": " Nice ",
        "rating": "5",
        "date": "2026-05-14",
        "platform": "app_store",
        "app_version": "4.3.3",
    }
    normalized, reason = normalize_review(record, 1)
    assert reason == "valid"
    assert normalized["review_text"] == "This is a great app for daily payments"
    assert normalized["rating"] == 5
    assert normalized["rating_label"] == "positive"
    assert normalized["date"] == "2026-05-14"
    assert normalized["platform"] == "app_store"
    assert normalized["review_id"] == "app_store-2026-05-14-00001"
    print("  PASS: test_normalize_review_standard_record")


def test_normalize_review_alias_fields():
    record = {
        "content": "Payment failed repeatedly during checkout at the store",
        "title": "Bad payment",
        "score": "1",
        "created_at": "05/14/2026",
        "store": "Android",
        "appVersion": "4.3.3",
        "thumbsUpCount": "12",
    }
    normalized, reason = normalize_review(record, 2)
    assert reason == "valid"
    assert normalized["review_text"] == "Payment failed repeatedly during checkout at the store"
    assert normalized["review_title"] == "Bad payment"
    assert normalized["rating"] == 1
    assert normalized["rating_label"] == "negative"
    assert normalized["platform"] == "play_store"
    assert normalized["thumbs_up_count"] == 12
    print("  PASS: test_normalize_review_alias_fields")


def test_normalize_review_rejects_bad_record():
    record = {
        "review_text": "",
        "rating": "5",
        "date": "2026-05-14",
        "platform": "app_store",
    }
    normalized, reason = normalize_review(record, 1)
    assert normalized is None
    assert reason == "missing review_text"
    print("  PASS: test_normalize_review_rejects_bad_record")


def test_normalize_review_rejects_short_review():
    record = {
        "review_text": "Good app works well today",
        "rating": "5",
        "date": "2026-05-14",
        "platform": "app_store",
    }
    normalized, reason = normalize_review(record, 1)
    assert normalized is None
    assert reason == "review_text has fewer than 6 words"
    print("  PASS: test_normalize_review_rejects_short_review")


def test_normalize_review_rejects_emoji():
    record = {
        "review_text": "This app works really well for daily payments 😊",
        "rating": "5",
        "date": "2026-05-14",
        "platform": "app_store",
    }
    normalized, reason = normalize_review(record, 1)
    assert normalized is None
    assert reason == "review contains emoji"
    print("  PASS: test_normalize_review_rejects_emoji")


def test_normalize_review_rejects_non_english():
    record = {
        "review_text": "यह ऐप भुगतान के लिए बहुत अच्छा काम करता है",
        "rating": "5",
        "date": "2026-05-14",
        "platform": "app_store",
    }
    normalized, reason = normalize_review(record, 1)
    assert normalized is None
    assert reason == "non-English review_text"
    print("  PASS: test_normalize_review_rejects_non_english")


def test_remove_duplicate_reviews():
    reviews = [
        {"review_text": "Great app", "date": "2026-05-14", "platform": "app_store", "rating": 5},
        {"review_text": "Great app", "date": "2026-05-14", "platform": "app_store", "rating": 5},
        {"review_text": "Bad app", "date": "2026-05-14", "platform": "app_store", "rating": 1},
    ]
    unique, count = remove_duplicate_reviews(reviews)
    assert len(unique) == 2
    assert count == 1
    print("  PASS: test_remove_duplicate_reviews")


def test_normalize_reviews_report():
    records = [
        {"review_text": "This app works great for all my payments", "rating": "5", "date": "2026-05-14", "platform": "app_store"},
        {"review_text": "Payment failed repeatedly during checkout at the store", "rating": "1", "date": "2026-05-14", "platform": "play_store"},
        {"review_text": "", "rating": "3", "date": "2026-05-14", "platform": "app_store"},
    ]
    normalized, report = normalize_reviews(records)
    assert len(normalized) == 2
    assert report["input_count"] == 3
    assert report["rejected_count"] == 1
    assert report["final_count"] == 2
    assert report["platform_counts"]["app_store"] == 1
    assert report["platform_counts"]["play_store"] == 1
    print("  PASS: test_normalize_reviews_report")


def run_all_tests():
    print("=" * 50)
    print("Phase 3 Normalization Tests")
    print("=" * 50)

    tests = [
        test_normalize_text,
        test_normalize_date,
        test_normalize_rating,
        test_rating_label,
        test_normalize_platform,
        test_normalize_integer,
        test_quality_helpers,
        test_normalize_review_standard_record,
        test_normalize_review_alias_fields,
        test_normalize_review_rejects_bad_record,
        test_normalize_review_rejects_short_review,
        test_normalize_review_rejects_emoji,
        test_normalize_review_rejects_non_english,
        test_remove_duplicate_reviews,
        test_normalize_reviews_report,
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
