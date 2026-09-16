"""
Phase 3: Data Normalization and Cleanup

Converts ingested review data from Phase 2 into a consistent structure for
privacy filtering and AI analysis.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


STANDARD_FIELDS = [
    "review_id",
    "review_text",
    "review_title",
    "rating",
    "rating_label",
    "date",
    "platform",
    "app_version",
    "language",
    "thumbs_up_count",
    "source",
]

FIELD_ALIASES = {
    "review_text": ["review_text", "content", "body", "text", "review", "comment"],
    "review_title": ["review_title", "title", "subject", "heading"],
    "rating": ["rating", "stars", "score", "star_rating"],
    "date": ["date", "review_date", "created_at", "posted_at", "timestamp"],
    "platform": ["platform", "source_platform", "store"],
    "app_version": ["app_version", "version", "appVersion"],
    "language": ["language", "lang", "locale"],
    "thumbs_up_count": ["thumbs_up_count", "thumbsUpCount", "helpful_count", "helpful"],
}

DATE_FORMATS = [
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%B %d, %Y",
]

PLATFORM_ALIASES = {
    "app store": "app_store",
    "app_store": "app_store",
    "ios": "app_store",
    "apple": "app_store",
    "play store": "play_store",
    "play_store": "play_store",
    "google_play": "play_store",
    "android": "play_store",
    "google": "play_store",
}

MIN_REVIEW_WORDS = 6
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002700-\U000027BF"
    "\U00002600-\U000026FF"
    "]+",
    flags=re.UNICODE,
)


# --- Generic Field Helpers ---

def get_first_available_value(record, canonical_field):
    """Get a field value using known aliases for platform-specific exports."""
    for field_name in FIELD_ALIASES.get(canonical_field, [canonical_field]):
        if field_name in record and record[field_name] not in (None, ""):
            return record[field_name]
    return ""


def normalize_text(value):
    """Normalize text by trimming whitespace and collapsing repeated spaces."""
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def normalize_date(value):
    """Normalize date into YYYY-MM-DD format."""
    value = normalize_text(value)
    if not value:
        return None

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def normalize_rating(value):
    """Normalize rating into an integer between 1 and 5."""
    try:
        rating = int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None

    if 1 <= rating <= 5:
        return rating
    return None


def get_rating_label(rating):
    """Create a readable rating sentiment label."""
    if rating is None:
        return "unknown"
    if rating <= 2:
        return "negative"
    if rating == 3:
        return "neutral"
    return "positive"


def normalize_platform(value):
    """Normalize platform name into app_store or play_store."""
    value = normalize_text(value).lower()
    return PLATFORM_ALIASES.get(value, value)


def normalize_integer(value, default=0):
    """Normalize numeric optional fields into integers."""
    if value in (None, ""):
        return default
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return default


def count_words(text):
    """Count words using alphabetic and numeric tokens."""
    return len(re.findall(r"\b[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?\b", text))


def contains_emoji(text):
    """Return True if the text contains emoji characters."""
    return bool(EMOJI_PATTERN.search(text or ""))


def is_english_text(text):
    """Return True if review text is compatible with English-only analysis."""
    if not text:
        return False
    ascii_chars = sum(1 for char in text if ord(char) < 128)
    total_chars = len(text)
    if total_chars == 0:
        return False
    ascii_ratio = ascii_chars / total_chars
    has_english_letters = bool(re.search(r"[A-Za-z]", text))
    return ascii_ratio >= 0.95 and has_english_letters


def build_review_id(platform, date, index):
    """Build a stable review ID for downstream processing."""
    return f"{platform}-{date}-{index:05d}"


# --- Normalization Pipeline ---

def normalize_review(record, index):
    """Normalize one review into the standard schema."""
    review_text = normalize_text(get_first_available_value(record, "review_text"))
    review_title = normalize_text(get_first_available_value(record, "review_title"))
    date = normalize_date(get_first_available_value(record, "date"))
    rating = normalize_rating(get_first_available_value(record, "rating"))
    platform = normalize_platform(get_first_available_value(record, "platform"))
    app_version = normalize_text(get_first_available_value(record, "app_version"))
    language = normalize_text(get_first_available_value(record, "language")) or "unknown"
    thumbs_up_count = normalize_integer(get_first_available_value(record, "thumbs_up_count"))

    if not review_text:
        return None, "missing review_text"
    if contains_emoji(review_text) or contains_emoji(review_title):
        return None, "review contains emoji"
    if not is_english_text(review_text):
        return None, "non-English review_text"
    if count_words(review_text) < MIN_REVIEW_WORDS:
        return None, "review_text has fewer than 6 words"
    if date is None:
        return None, "unusable date"
    if rating is None:
        return None, "unusable rating"
    if platform not in ("app_store", "play_store"):
        return None, "unusable platform"

    normalized = {
        "review_id": build_review_id(platform, date, index),
        "review_text": review_text,
        "review_title": review_title,
        "rating": rating,
        "rating_label": get_rating_label(rating),
        "date": date,
        "platform": platform,
        "app_version": app_version,
        "language": language,
        "thumbs_up_count": thumbs_up_count,
        "source": "phase2_ingested",
    }

    return normalized, "valid"


def remove_duplicate_reviews(reviews):
    """Remove duplicates based on review text, date, platform, and rating."""
    seen = set()
    unique_reviews = []
    duplicate_count = 0

    for review in reviews:
        key = (
            review["review_text"].lower(),
            review["date"],
            review["platform"],
            review["rating"],
        )
        if key in seen:
            duplicate_count += 1
            continue
        seen.add(key)
        unique_reviews.append(review)

    return unique_reviews, duplicate_count


def normalize_reviews(records):
    """Normalize a list of review records and return output plus report."""
    normalized_reviews = []
    rejected_records = []

    for index, record in enumerate(records, start=1):
        normalized, reason = normalize_review(record, index)
        if normalized is None:
            rejected_records.append({"index": index, "reason": reason})
        else:
            normalized_reviews.append(normalized)

    deduplicated_reviews, duplicate_count = remove_duplicate_reviews(normalized_reviews)

    platform_counts = {
        "app_store": sum(1 for r in deduplicated_reviews if r["platform"] == "app_store"),
        "play_store": sum(1 for r in deduplicated_reviews if r["platform"] == "play_store"),
    }

    rating_counts = {
        "negative": sum(1 for r in deduplicated_reviews if r["rating_label"] == "negative"),
        "neutral": sum(1 for r in deduplicated_reviews if r["rating_label"] == "neutral"),
        "positive": sum(1 for r in deduplicated_reviews if r["rating_label"] == "positive"),
    }

    report = {
        "input_count": len(records),
        "normalized_count": len(normalized_reviews),
        "rejected_count": len(rejected_records),
        "rejected_records": rejected_records,
        "duplicates_removed": duplicate_count,
        "final_count": len(deduplicated_reviews),
        "platform_counts": platform_counts,
        "rating_label_counts": rating_counts,
        "standard_fields": STANDARD_FIELDS,
    }

    return deduplicated_reviews, report


# --- File IO ---

def load_json(path):
    """Load JSON review records."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    """Save data as JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --- Entry Point ---

def main():
    """Run Phase 3 normalization using Phase 2 ingested output."""
    project_root = Path(__file__).resolve().parent.parent
    input_path = project_root / "phase2" / "data" / "ingested" / "ingested_reviews.json"
    output_dir = project_root / "phase3" / "data" / "normalized"
    output_path = output_dir / "normalized_reviews.json"
    report_path = output_dir / "normalization_report.json"

    if not input_path.exists():
        print(f"Phase 2 ingested data not found: {input_path}")
        print("Run: python phase2/ingest_reviews.py")
        sys.exit(1)

    print("=" * 60)
    print("Phase 3: Data Normalization and Cleanup")
    print("=" * 60)
    print(f"\nLoading ingested reviews from: {input_path}")

    records = load_json(str(input_path))
    normalized_reviews, report = normalize_reviews(records)

    save_json(normalized_reviews, str(output_path))
    save_json(report, str(report_path))

    print(f"\nInput reviews: {report['input_count']}")
    print(f"Normalized reviews: {report['normalized_count']}")
    print(f"Rejected records: {report['rejected_count']}")
    print(f"Duplicates removed: {report['duplicates_removed']}")
    print(f"Final normalized reviews: {report['final_count']}")
    print(f"\nPlatform counts: {report['platform_counts']}")
    print(f"Rating label counts: {report['rating_label_counts']}")
    print(f"\nNormalized reviews saved to: {output_path}")
    print(f"Normalization report saved to: {report_path}")
    print("\n" + "=" * 60)
    print("Normalization complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
