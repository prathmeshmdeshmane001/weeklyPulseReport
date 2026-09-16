# Phase 4: Privacy Protection and Safety Review

## Objective

Remove or mask personally identifiable information from normalized review data before AI analysis.

## Contents

```text
phase4/
├── privacy_filter.py                  # Main privacy filtering script
├── README.md                          # This file
└── data/
    └── privacy_safe/                  # Output generated after running Phase 4
        ├── privacy_safe_reviews.json  # Reviews safe for AI analysis
        └── privacy_report.json        # PII detection and masking summary
```

## How to Run

From the project root:

```bash
python phase4/privacy_filter.py
```

## Input

Phase 4 reads the Phase 3 output:

```text
phase3/data/normalized/normalized_reviews.json
```

## Output

Phase 4 writes:

```text
phase4/data/privacy_safe/privacy_safe_reviews.json
phase4/data/privacy_safe/privacy_report.json
```

## PII Types Checked

The privacy filter scans review text and review titles for:

- Email addresses
- Phone numbers
- Usernames / handles
- IP addresses
- Account IDs
- Order, ticket, case, and reference IDs
- Device IDs, IMEI, and serial numbers
- Long numeric IDs
- Physical address-like strings
- Full-name phrases such as `my name is First Last`

## What the Script Does

1. Loads normalized reviews from Phase 3
2. Scans `review_text` and `review_title` for PII patterns
3. Replaces detected PII with safe placeholders such as `[EMAIL]` or `[PHONE]`
4. Marks each review with `privacy_checked`, `pii_detected`, and `pii_types_detected`
5. Runs a second validation pass to confirm no known PII remains
6. Generates a privacy report
7. Saves a privacy-safe dataset for Phase 5 AI analysis

## Status

Complete — privacy filtering, validation, reporting, and tests are implemented.
