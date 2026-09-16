"""
Phase 2: Groww Google Play Public Review Fetcher

Fetches public-facing Groww reviews from Google Play using the google-play-scraper
package and saves them as a raw CSV file for the standard ingestion pipeline.
"""

import argparse
import csv
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


GROWW_PACKAGE_NAME = "com.nextbillion.groww"
DEFAULT_COUNTRY = "in"
DEFAULT_LANGUAGE = "en"
DEFAULT_TARGET_COUNT = 2500
DEFAULT_WEEKS = 12


def import_google_play_scraper():
    try:
        from google_play_scraper import Sort, reviews
        return Sort, reviews
    except ImportError:
        print("Missing dependency: google-play-scraper")
        print("Install it with: pip install google-play-scraper")
        sys.exit(1)


def format_date(value):
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if value:
        return str(value)
    return ""


def map_review(raw_review):
    return {
        "review_text": raw_review.get("content", ""),
        "review_title": "",
        "rating": raw_review.get("score", ""),
        "date": format_date(raw_review.get("at")),
        "platform": "play_store",
        "app_version": raw_review.get("reviewCreatedVersion", ""),
        "language": DEFAULT_LANGUAGE,
        "thumbs_up_count": raw_review.get("thumbsUpCount", 0),
        "review_id": raw_review.get("reviewId", ""),
        "source_app": "Groww",
        "source_package": GROWW_PACKAGE_NAME,
        "source_method": "google_play_public_no_login_fetcher",
    }


def fetch_reviews(package_name, country, language, target_count, weeks):
    Sort, reviews = import_google_play_scraper()
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    fetched_reviews = []
    continuation_token = None

    while len(fetched_reviews) < target_count:
        batch, continuation_token = reviews(
            package_name,
            lang=language,
            country=country,
            sort=Sort.NEWEST,
            count=min(200, target_count - len(fetched_reviews)),
            continuation_token=continuation_token,
        )

        if not batch:
            break

        stop_fetching = False
        for raw_review in batch:
            review_date = raw_review.get("at")
            if isinstance(review_date, datetime) and review_date < cutoff_date:
                stop_fetching = True
                continue
            fetched_reviews.append(map_review(raw_review))

        print(f"Fetched {len(fetched_reviews)} reviews so far...")

        if stop_fetching or continuation_token is None:
            break

    return fetched_reviews[:target_count]


def save_reviews_csv(reviews, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fieldnames = [
        "review_text",
        "review_title",
        "rating",
        "date",
        "platform",
        "app_version",
        "language",
        "thumbs_up_count",
        "review_id",
        "source_app",
        "source_package",
        "source_method",
    ]
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reviews)


def main():
    parser = argparse.ArgumentParser(description="Fetch public Groww Google Play reviews.")
    parser.add_argument("--package", default=GROWW_PACKAGE_NAME, help="Google Play package name")
    parser.add_argument("--country", default=DEFAULT_COUNTRY, help="Google Play country code")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE, help="Review language code")
    parser.add_argument("--count", type=int, default=DEFAULT_TARGET_COUNT, help="Target number of reviews")
    parser.add_argument("--weeks", type=int, default=DEFAULT_WEEKS, help="Recent review window in weeks")
    parser.add_argument("--output", default="", help="Output CSV path")
    args = parser.parse_args()

    phase2_dir = Path(__file__).parent
    default_output = phase2_dir / "data" / "raw" / "groww_play_store_reviews.csv"
    output_path = Path(args.output) if args.output else default_output

    print("=" * 60)
    print("Phase 2: Groww Google Play Public Review Fetcher")
    print("=" * 60)
    print(f"Package: {args.package}")
    print(f"Country: {args.country}")
    print(f"Language: {args.language}")
    print(f"Target count: {args.count}")
    print(f"Window: last {args.weeks} weeks")

    fetched_reviews = fetch_reviews(
        package_name=args.package,
        country=args.country,
        language=args.language,
        target_count=args.count,
        weeks=args.weeks,
    )

    save_reviews_csv(fetched_reviews, str(output_path))

    print(f"\nSaved {len(fetched_reviews)} reviews to: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
