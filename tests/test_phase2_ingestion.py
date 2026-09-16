"""
Tests for Phase 2: Review Data Ingestion

Validates that the ingestion pipeline correctly loads, validates, filters,
and deduplicates review data.
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path so we can import from phase2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from phase2.ingest_reviews import (
    parse_date,
    is_within_review_window,
    validate_review,
    filter_by_date_window,
    remove_duplicates,
    load_csv,
)


def test_parse_date_valid_formats():
    """Test that various date formats are parsed correctly."""
    assert parse_date("2026-04-15") is not None
    assert parse_date("04/15/2026") is not None
    assert parse_date("15/04/2026") is not None
    assert parse_date("April 15, 2026") is not None
    print("  PASS: test_parse_date_valid_formats")


def test_parse_date_invalid():
    """Test that invalid dates return None."""
    assert parse_date("") is None
    assert parse_date(None) is None
    assert parse_date("not-a-date") is None
    print("  PASS: test_parse_date_invalid")


def test_is_within_review_window():
    """Test date window filtering."""
    now = datetime(2026, 5, 14)
    recent = datetime(2026, 4, 1)
    old = datetime(2025, 1, 1)

    assert is_within_review_window(recent, reference_date=now, weeks=12) is True
    assert is_within_review_window(old, reference_date=now, weeks=12) is False
    print("  PASS: test_is_within_review_window")


def test_validate_review_valid():
    """Test that a valid review passes validation."""
    review = {
        "review_text": "Great app!",
        "rating": "5",
        "date": "2026-04-10",
        "platform": "app_store",
    }
    is_valid, reason = validate_review(review)
    assert is_valid is True
    print("  PASS: test_validate_review_valid")


def test_validate_review_missing_text():
    """Test that a review with empty text is rejected."""
    review = {
        "review_text": "",
        "rating": "5",
        "date": "2026-04-10",
        "platform": "app_store",
    }
    is_valid, reason = validate_review(review)
    assert is_valid is False
    assert "review_text" in reason
    print("  PASS: test_validate_review_missing_text")


def test_validate_review_bad_rating():
    """Test that a review with out-of-range rating is rejected."""
    review = {
        "review_text": "Good app",
        "rating": "7",
        "date": "2026-04-10",
        "platform": "app_store",
    }
    is_valid, reason = validate_review(review)
    assert is_valid is False
    assert "rating" in reason
    print("  PASS: test_validate_review_bad_rating")


def test_validate_review_bad_platform():
    """Test that a review with invalid platform is rejected."""
    review = {
        "review_text": "Good app",
        "rating": "4",
        "date": "2026-04-10",
        "platform": "unknown_store",
    }
    is_valid, reason = validate_review(review)
    assert is_valid is False
    assert "platform" in reason
    print("  PASS: test_validate_review_bad_platform")


def test_remove_duplicates():
    """Test that duplicate reviews are removed."""
    reviews = [
        {"review_text": "Great app", "date": "2026-04-10", "platform": "app_store"},
        {"review_text": "Great app", "date": "2026-04-10", "platform": "app_store"},
        {"review_text": "Bad app", "date": "2026-04-10", "platform": "app_store"},
    ]
    unique, dup_count = remove_duplicates(reviews)
    assert len(unique) == 2
    assert dup_count == 1
    print("  PASS: test_remove_duplicates")


def test_filter_by_date_window():
    """Test that old reviews are filtered out."""
    now = datetime(2026, 5, 14)
    reviews = [
        {"date": "2026-04-10"},
        {"date": "2026-03-01"},
        {"date": "2025-01-01"},
    ]
    filtered, excluded = filter_by_date_window(reviews, reference_date=now, weeks=12)
    assert len(filtered) == 2
    assert excluded == 1
    print("  PASS: test_filter_by_date_window")


def test_load_sample_csv():
    """Test that sample CSV files load correctly."""
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "phase2", "data", "raw")
    sample_dir = os.path.join(os.path.dirname(__file__), "..", "phase2", "data", "sample")

    app_store_path = os.path.join(raw_dir, "app_store_reviews.csv")
    if not os.path.exists(app_store_path):
        app_store_path = os.path.join(sample_dir, "app_store_reviews.csv")

    play_store_path = os.path.join(raw_dir, "play_store_reviews.csv")
    if not os.path.exists(play_store_path):
        play_store_path = os.path.join(sample_dir, "play_store_reviews.csv")

    groww_play_path = os.path.join(raw_dir, "groww_play_store_reviews.csv")

    if os.path.exists(app_store_path):
        reviews = load_csv(app_store_path)
        assert len(reviews) > 0
        assert "review_text" in reviews[0]
        print(f"  PASS: test_load_sample_csv (app_store: {len(reviews)} reviews)")

    if os.path.exists(play_store_path):
        reviews = load_csv(play_store_path)
        assert len(reviews) > 0
        assert "review_text" in reviews[0]
        print(f"  PASS: test_load_sample_csv (play_store: {len(reviews)} reviews)")

    if os.path.exists(groww_play_path):
        reviews = load_csv(groww_play_path)
        assert len(reviews) > 0
        assert "review_text" in reviews[0]
        print(f"  PASS: test_load_sample_csv (groww_play_store: {len(reviews)} reviews)")


def run_all_tests():
    """Run all Phase 2 ingestion tests."""
    print("=" * 50)
    print("Phase 2 Ingestion Tests")
    print("=" * 50)

    tests = [
        test_parse_date_valid_formats,
        test_parse_date_invalid,
        test_is_within_review_window,
        test_validate_review_valid,
        test_validate_review_missing_text,
        test_validate_review_bad_rating,
        test_validate_review_bad_platform,
        test_remove_duplicates,
        test_filter_by_date_window,
        test_load_sample_csv,
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
