# Weekly Pulse Output Schema

## Overview

This document defines the structure and content of the weekly feedback pulse that the AI agent generates. This is the final report published to Google Docs and included in the Gmail draft.

## Report Sections

The weekly pulse must contain the following sections in order:

### 1. Title

- Format: `Weekly Review Pulse — [Product Name]`
- Example: `Weekly Review Pulse — MyFinanceApp`

### 2. Date Range

- The start and end dates of the review period covered
- Format: `[Start Date] to [End Date]`
- Example: `March 4, 2026 to April 28, 2026`

### 3. Top 3 Themes

Each theme entry should include:

| Element | Description |
|---------|-------------|
| Theme name | Short descriptive label (e.g., "Payment Failures") |
| Theme summary | 1–2 sentence explanation of what users are saying |
| Review count | Approximate number of reviews supporting this theme |

Example:

```text
Theme: Payment Failures
Summary: Multiple users report that payments fail or get stuck during checkout. This is especially common on Android devices.
Reviews: ~42
```

### 4. User Quotes

- Exactly **3 real user quotes**
- Each quote must be a **verbatim snippet** from a review after privacy cleanup
- No invented, paraphrased, or AI-generated quotes
- Each quote should indicate which theme it supports

Example:

```text
Quote: "Every time I try to pay, the app just freezes and I have to restart."
Theme: Payment Failures
```

### 5. Action Ideas

- Exactly **3 action ideas**
- Each action should be concrete and grounded in a theme
- Avoid vague suggestions like "improve the app"

Example:

```text
Action: Investigate payment gateway timeout on Android and add retry logic.
Theme: Payment Failures
```

### 6. Summary

- A short closing paragraph (2–3 sentences)
- Highlights the overall user sentiment for the week
- Mentions any urgent or notable trends

## Constraints

- **Maximum themes in report:** 3 (selected from up to 5 clustered themes)
- **Quotes:** 3, all real and privacy-safe
- **Actions:** 3, all connected to a theme
- **Total length:** Concise, scannable, ideally under 250 words for the core content
- **No PII:** No usernames, emails, device IDs, or other identifiers

## Output Destinations

| Destination | Method | Content |
|-------------|--------|---------|
| Google Docs | MCP server | Full weekly pulse document |
| Gmail | MCP server | Draft email with the pulse or a link to the Docs report |

## Output Format

The pulse should be formatted as clean, readable text suitable for:

- Google Docs (structured with headings and lists)
- Email body (plain text or simple HTML)

No complex formatting, charts, or embedded media is required.
