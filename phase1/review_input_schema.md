# Review Input Schema

## Overview

This document defines the expected format and fields for the review data that the system will process. Reviews come from public App Store and Play Store exports.

## Source Platforms

- **Apple App Store** — public review export
- **Google Play Store** — public review export

## Required Fields

These fields must be present for a review to be processed:

| Field | Type | Description |
|-------|------|-------------|
| `review_text` | String | The actual review content written by the user |
| `rating` | Integer (1–5) | Star rating given by the reviewer |
| `date` | Date (YYYY-MM-DD) | Date the review was posted |
| `platform` | String | Source platform: `app_store` or `play_store` |

## Optional Fields

These fields are used if available but are not mandatory:

| Field | Type | Description |
|-------|------|-------------|
| `review_title` | String | Short heading or subject of the review |
| `app_version` | String | Version of the app the review applies to |
| `language` | String | Language of the review (e.g., `en`) |
| `thumbs_up_count` | Integer | Number of users who found the review helpful |

## Time Range

- Only reviews from the **last 8–12 weeks** should be included in each weekly analysis
- Reviews outside this window should be excluded during ingestion

## Data Quality Rules

A review is **excluded** if:

- `review_text` is empty or missing
- `date` is missing or cannot be parsed
- `rating` is outside the 1–5 range
- The review is a duplicate of another entry

## File Format

The system should support review exports in one or more of:

- **CSV** — comma-separated values with a header row
- **JSON** — array of review objects
- **XLSX** — spreadsheet format (if applicable)

## Sample Review Record

```json
{
  "review_text": "The app crashes every time I try to withdraw money. Very frustrating.",
  "review_title": "Crashes on withdrawal",
  "rating": 1,
  "date": "2026-03-15",
  "platform": "play_store",
  "app_version": "4.2.1"
}
```

## Platform-Specific Notes

### App Store

- May use `title` instead of `review_title`
- Date format may vary (e.g., `MM/DD/YYYY`)
- Rating may appear as `stars` or `score`

### Play Store

- May include `thumbsUpCount` for helpfulness
- Date may appear as ISO format or localized string
- `review_text` may be labeled `content` or `body`

## Normalization Responsibility

Field mapping and format standardization happen in **Phase 3** (`phase3/`). The ingestion phase only loads raw data and applies basic date-range and completeness filters.
