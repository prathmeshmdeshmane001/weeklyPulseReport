# Phase 10: Gmail MCP Draft Creation

## Objective

Create a Gmail draft containing the weekly pulse or a link to the Google Docs report.

## Prerequisites

Before running Phase 10, add the recipient email to your `.env` file:

```text
EMAIL_RECIPIENT=your_email@example.com
```

## How to Run

```bash
python phase10/create_email_draft.py
```

## What It Does

1. Reads the weekly pulse JSON from `phase8/data/weekly_pulse/weekly_pulse.json`
2. Reads the Google Doc URL from Phase 9 status (if available)
3. Formats an email with:
   - Headline summary
   - Top 3 themes with descriptions
   - Key user quotes
   - Recommended actions
   - Link to full Google Doc report (if Phase 9 succeeded)
4. Creates a Gmail draft via MCP
5. Saves status to `phase10/data/gmail_delivery/phase10_gmail_status.json`

## Output

- **Gmail Draft**: Created in your Gmail account
- **Status JSON**: `phase10/data/gmail_delivery/phase10_gmail_status.json`
  - `success`: true/false
  - `recipient`: Email address
  - `subject`: Email subject line
  - `timestamp`: When it was created

## MCP Server

- **URL**: https://saksham-mcp-server-production-7819.up.railway.app
- **Tool Used**: `create_email_draft`

## Files

- `create_email_draft.py` - Main script for creating Gmail draft
- `data/gmail_delivery/` - Output directory for delivery status

## Email Format

The email includes:
- Professional greeting
- Headline summary of weekly sentiment
- Top 3 themes with descriptions
- 3 real user quotes
- 3 recommended action ideas
- Link to full Google Docs report
- Professional signature
