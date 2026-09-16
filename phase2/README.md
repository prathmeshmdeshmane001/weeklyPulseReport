# Phase 2: Review Data Collection

## Objective

Load public App Store and Play Store review exports, validate required fields, filter by the 8–12 week date window, remove incomplete and duplicate entries, and produce a clean ingested dataset for Phase 3.

## Contents

```text
phase2/
├── ingest_reviews.py              # Main ingestion script
├── fetch_groww_play_reviews.py    # Live Google Play review fetcher
├── README.md                      # This file
└── data/
    ├── raw/                       # Source review export files
    │   ├── app_store_reviews.csv  # Sample App Store reviews
    │   └── play_store_reviews.csv # Sample Play Store reviews
    └── ingested/                  # Output (created after running ingestion)
        ├── ingested_reviews.json  # Clean ingested reviews
        └── ingestion_report.json  # Ingestion summary and statistics
```

## How to Run

### Option 1: Ingest from CSV files
```bash
python phase2/ingest_reviews.py
```

### Option 2: Fetch live reviews from Google Play
```bash
python phase2/fetch_groww_play_reviews.py --count 500 --weeks 2
```

### Option 3: Full pipeline with live fetch
```bash
# First fetch new reviews
python phase2/fetch_groww_play_reviews.py

# Then ingest them
python phase2/ingest_reviews.py
```

## What the Ingestion Script Does

1. **Discovers review files** — finds all `.csv` and `.json` files in `data/raw/`
2. **Loads reviews** — reads each file and collects all review records
3. **Validates required fields** — checks `review_text`, `rating`, `date`, `platform`
4. **Filters by date window** — keeps only reviews from the last 12 weeks
5. **Removes duplicates** — deduplicates by review text + date + platform
6. **Saves output** — writes `ingested_reviews.json` and `ingestion_report.json`

## Live Review Fetching (Google Play)

The `fetch_groww_play_reviews.py` script fetches **live reviews** from the Google Play Store using the `google-play-scraper` library.

### Features:
- **No API key required** — uses public web scraping
- **Configurable** — adjust count, country, language, time window
- **Automatic deduplication** — by review ID
- **Saves as CSV** — ready for ingestion

### Usage:
```bash
# Fetch 500 most recent reviews from last 2 weeks
python phase2/fetch_groww_play_reviews.py --count 500 --weeks 2

# Fetch 1000 reviews from last month (default 12 weeks)
python phase2/fetch_groww_play_reviews.py --count 1000
```

### Parameters:
- `--count`: Number of reviews to fetch (default: 2500)
- `--weeks`: How many weeks back to fetch (default: 12)
- `--country`: Country code (default: 'in' for India)
- `--language`: Language code (default: 'en')

### GitHub Actions Integration:
The workflow automatically fetches new reviews every week:
```yaml
- name: Fetch latest reviews
  run: |
    python phase2/fetch_groww_play_reviews.py --count 500 --weeks 2
```

## Sample Data

The `data/raw/` folder contains sample review CSVs with:

- **16 App Store reviews** (includes 1 empty text, 1 old review to test filtering)
- **16 Play Store reviews** (includes 1 empty/missing rating, 1 old review to test filtering)

## Validation Rules (from Phase 1 schema)

- `review_text` must be non-empty
- `date` must be parseable
- `rating` must be an integer between 1 and 5
- `platform` must be `app_store` or `play_store`
- Reviews outside the 12-week window are excluded
- Duplicate entries are removed

## Status

✅ **Complete** — Ingestion script implemented
✅ **Complete** — Live Google Play review fetcher implemented
✅ **Complete** — GitHub Actions integration for weekly automated fetching
