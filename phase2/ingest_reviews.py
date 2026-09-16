"""
Phase 2: Review Data Ingestion

Loads public App Store and Play Store review exports, validates required fields,
filters by the 8-12 week date window, removes incomplete entries, and produces
a clean ingested dataset ready for Phase 3 normalization.
"""

import csv
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


# --- Configuration ---

REQUIRED_FIELDS = ["review_text", "rating", "date", "platform"]
OPTIONAL_FIELDS = ["review_title", "app_version", "language", "thumbs_up_count"]
VALID_PLATFORMS = ["app_store", "play_store"]
MIN_RATING = 1
MAX_RATING = 5
REVIEW_WINDOW_WEEKS = 12  # Include reviews from the last N weeks

# Date formats to try when parsing review dates
DATE_FORMATS = [
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%B %d, %Y",
]


# --- Date Parsing ---

def parse_date(date_string):
    """Try multiple date formats and return a datetime object or None."""
    if not date_string or not date_string.strip():
        return None
    date_string = date_string.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    return None


def is_within_review_window(review_date, reference_date=None, weeks=REVIEW_WINDOW_WEEKS):
    """Check if a review date falls within the allowed time window."""
    if reference_date is None:
        reference_date = datetime.now()
    cutoff = reference_date - timedelta(weeks=weeks)
    return review_date >= cutoff


# --- Validation ---

def validate_review(review, line_number=None):
    """
    Validate a single review record.
    Returns (is_valid, reason) tuple.
    """
    # Check review_text is present and non-empty
    review_text = review.get("review_text", "").strip()
    if not review_text:
        return False, "missing or empty review_text"

    # Check date is present and parseable
    raw_date = review.get("date", "")
    parsed_date = parse_date(raw_date)
    if parsed_date is None:
        return False, f"missing or unparseable date: '{raw_date}'"

    # Check rating is present and in range
    try:
        rating = int(review.get("rating", ""))
    except (ValueError, TypeError):
        return False, f"missing or invalid rating: '{review.get('rating', '')}'"
    if rating < MIN_RATING or rating > MAX_RATING:
        return False, f"rating {rating} out of range ({MIN_RATING}-{MAX_RATING})"

    # Check platform is present and valid
    platform = review.get("platform", "").strip().lower()
    if platform not in VALID_PLATFORMS:
        return False, f"invalid platform: '{platform}'"

    return True, "valid"


def filter_by_date_window(reviews, reference_date=None, weeks=REVIEW_WINDOW_WEEKS):
    """Filter reviews to only include those within the date window."""
    included = []
    excluded_count = 0
    for review in reviews:
        parsed_date = parse_date(review.get("date", ""))
        if parsed_date and is_within_review_window(parsed_date, reference_date, weeks):
            included.append(review)
        else:
            excluded_count += 1
    return included, excluded_count


def remove_duplicates(reviews):
    """Remove duplicate reviews based on review_text + date + platform."""
    seen = set()
    unique = []
    duplicate_count = 0
    for review in reviews:
        key = (
            review.get("review_text", "").strip().lower(),
            review.get("date", "").strip(),
            review.get("platform", "").strip().lower(),
        )
        if key not in seen:
            seen.add(key)
            unique.append(review)
        else:
            duplicate_count += 1
    return unique, duplicate_count


# --- File Loading ---

def load_csv(file_path):
    """Load reviews from a CSV file."""
    reviews = []
    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            reviews.append(dict(row))
    return reviews


def load_json(file_path):
    """Load reviews from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "reviews" in data:
        return data["reviews"]
    else:
        raise ValueError(f"Unexpected JSON structure in {file_path}")


def load_reviews(file_path):
    """Load reviews from a file based on its extension."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()
    if ext == ".csv":
        return load_csv(file_path)
    elif ext == ".json":
        return load_json(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Use .csv or .json")


# --- Main Ingestion Pipeline ---

def ingest_reviews(file_paths, reference_date=None, weeks=REVIEW_WINDOW_WEEKS):
    """
    Main ingestion function.
    Loads reviews from one or more files, validates, filters by date, removes duplicates.
    Returns the clean review list and an ingestion report.
    """
    all_reviews = []
    load_errors = []

    # Step 1: Load all review files
    for file_path in file_paths:
        try:
            reviews = load_reviews(file_path)
            print(f"  Loaded {len(reviews)} reviews from {file_path}")
            all_reviews.extend(reviews)
        except Exception as e:
            load_errors.append({"file": file_path, "error": str(e)})
            print(f"  ERROR loading {file_path}: {e}")

    total_loaded = len(all_reviews)
    print(f"\nTotal reviews loaded: {total_loaded}")

    # Step 2: Validate required fields
    valid_reviews = []
    invalid_reviews = []
    for i, review in enumerate(all_reviews):
        is_valid, reason = validate_review(review, line_number=i + 1)
        if is_valid:
            valid_reviews.append(review)
        else:
            invalid_reviews.append({"index": i + 1, "reason": reason})
            print(f"  Excluded review #{i+1}: {reason}")

    print(f"\nValid reviews: {len(valid_reviews)}")
    print(f"Invalid reviews: {len(invalid_reviews)}")

    # Step 3: Filter by date window
    date_filtered, date_excluded = filter_by_date_window(
        valid_reviews, reference_date, weeks
    )
    print(f"\nWithin {weeks}-week window: {len(date_filtered)}")
    print(f"Outside date window: {date_excluded}")

    # Step 4: Remove duplicates
    final_reviews, duplicate_count = remove_duplicates(date_filtered)
    print(f"\nDuplicates removed: {duplicate_count}")
    print(f"Final ingested reviews: {len(final_reviews)}")

    # Build ingestion report
    report = {
        "total_files": len(file_paths),
        "total_loaded": total_loaded,
        "valid_reviews": len(valid_reviews),
        "invalid_reviews": len(invalid_reviews),
        "invalid_details": invalid_reviews,
        "within_date_window": len(date_filtered),
        "outside_date_window": date_excluded,
        "duplicates_removed": duplicate_count,
        "final_count": len(final_reviews),
        "load_errors": load_errors,
    }

    return final_reviews, report


def save_ingested_reviews(reviews, output_path):
    """Save the ingested reviews to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)
    print(f"\nIngested reviews saved to: {output_path}")


def save_ingestion_report(report, output_path):
    """Save the ingestion report to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Ingestion report saved to: {output_path}")


# --- Entry Point ---

def main():
    """Run the ingestion pipeline on the sample review data."""
    phase2_dir = Path(__file__).parent
    raw_dir = phase2_dir / "data" / "raw"
    output_dir = phase2_dir / "data" / "ingested"

    # Discover all CSV and JSON files in the raw data directory
    review_files = sorted(
        [str(f) for f in raw_dir.iterdir() if f.suffix.lower() in (".csv", ".json")]
    )

    if not review_files:
        print("No review files found in", raw_dir)
        sys.exit(1)

    print("=" * 60)
    print("Phase 2: Review Data Ingestion")
    print("=" * 60)
    print(f"\nFound {len(review_files)} review file(s):")
    for f in review_files:
        print(f"  - {f}")
    print()

    # Run ingestion
    reviews, report = ingest_reviews(review_files)

    # Save outputs
    save_ingested_reviews(reviews, str(output_dir / "ingested_reviews.json"))
    save_ingestion_report(report, str(output_dir / "ingestion_report.json"))

    print("\n" + "=" * 60)
    print("Ingestion complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
