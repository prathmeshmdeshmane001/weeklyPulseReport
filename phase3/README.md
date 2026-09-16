# Phase 3: Data Normalization and Cleanup

## Objective

Convert Phase 2 ingested review data into a clean, predictable, and consistent structure before privacy filtering and AI analysis.

## Contents

```text
phase3/
├── normalize_reviews.py                 # Main normalization script
├── README.md                            # This file
└── data/
    └── normalized/                      # Output generated after running Phase 3
        ├── normalized_reviews.json      # Standardized review dataset
        └── normalization_report.json    # Summary of normalization results
```

## How to Run

From the project root:

```bash
python phase3/normalize_reviews.py
```

## Input

Phase 3 reads the Phase 2 output:

```text
phase2/data/ingested/ingested_reviews.json
```

## Output

Phase 3 writes:

```text
phase3/data/normalized/normalized_reviews.json
phase3/data/normalized/normalization_report.json
```

## Standard Review Schema

Each normalized review contains:

| Field | Description |
|-------|-------------|
| `review_id` | Stable generated identifier for downstream phases |
| `review_text` | Cleaned review body text |
| `review_title` | Cleaned title if available |
| `rating` | Integer rating from 1 to 5 |
| `rating_label` | `negative`, `neutral`, or `positive` |
| `date` | Standard date format: `YYYY-MM-DD` |
| `platform` | `app_store` or `play_store` |
| `app_version` | App version if available |
| `language` | Review language if available, otherwise `unknown` |
| `thumbs_up_count` | Helpful vote count if available, otherwise `0` |
| `source` | Source marker: `phase2_ingested` |

## What the Script Does

1. Loads Phase 2 ingested review data
2. Maps platform-specific field aliases into common fields
3. Standardizes dates into `YYYY-MM-DD`
4. Standardizes ratings into integers from 1 to 5
5. Normalizes platform values into `app_store` or `play_store`
6. Preserves review text, title, app version, language, and helpful count
7. Removes reviews with fewer than 6 words
8. Removes reviews containing emojis
9. Removes non-English reviews
10. Removes blank, unusable, or duplicate records
11. Generates a normalization report

## Status

Complete — normalization script, output generation, and tests are implemented.
