# Privacy and Constraint Rules

## Overview

This document defines the privacy requirements and project constraints that must be followed throughout all phases of the project. These rules apply to every output the system produces, including intermediate data, the weekly pulse, the Google Docs document, and the Gmail draft.

## Privacy Rules

### Rule 1: No Personally Identifiable Information in Outputs

No final output artifact (weekly pulse, Google Docs document, Gmail draft) may contain:

- **Email addresses**
- **Phone numbers**
- **Full names or usernames**
- **Device identifiers** (IMEI, serial numbers, etc.)
- **Account numbers or IDs**
- **IP addresses**
- **Physical addresses**
- **Any other information that can identify a specific reviewer**

### Rule 2: Clean Reviews Before Analysis

PII must be removed or masked **before** the AI agent processes the review data. This ensures that:

- The agent does not learn or repeat PII
- Selected quotes are already privacy-safe
- No PII leaks into theme summaries or action ideas

### Rule 3: Quotes Must Be Anonymous

User quotes included in the weekly pulse must:

- Come from real reviews (verbatim, not invented)
- Have all PII removed before selection
- Not include any information that could identify the reviewer
- Not be attributed to a named individual

### Rule 4: No Scraping or Login-Protected Data

- Only **public review exports** may be used as data sources
- The system must not scrape app store pages
- The system must not access reviews behind login-protected systems
- The system must not use automated tools that violate platform terms of service

## Project Constraints

### Constraint 1: Theme Limits

- Maximum **5 themes** may be created during clustering
- Only the **top 3 themes** should appear in the weekly pulse

### Constraint 2: Quote Requirements

- Exactly **3 user quotes** in each weekly pulse
- All quotes must be **real** (from source review data)
- No paraphrasing or AI-generated substitute quotes

### Constraint 3: Action Ideas

- Exactly **3 action ideas** in each weekly pulse
- Each action must be **connected to a theme**
- Actions must be **concrete**, not vague

### Constraint 4: Report Length

- The weekly pulse should be **concise and scannable**
- Target length is approximately **250 words or less** for core content
- The report should fit on **one page** when viewed in Google Docs

### Constraint 5: MCP-First Integration

- Google Docs must be accessed through an **MCP server or connector**
- Gmail must be accessed through an **MCP server or connector**
- The project must **not** use custom OAuth clients or direct REST API integration as the primary path

## PII Detection Checklist

Before any review data is used in analysis or output, check for:

- [ ] Email patterns (e.g., `user@example.com`)
- [ ] Phone number patterns (e.g., `+1-555-123-4567`)
- [ ] Usernames or handles (e.g., `@username`)
- [ ] Device IDs or serial numbers
- [ ] Account or order numbers
- [ ] Full names mentioned in review text
- [ ] Physical addresses or location details

## Where These Rules Apply

| Phase | What Must Be Checked |
|-------|---------------------|
| Phase 2: Data Collection | Only public exports used |
| Phase 3: Normalization | No PII introduced during mapping |
| Phase 4: Privacy Filtering | PII actively removed from all reviews |
| Phase 5–7: AI Analysis | Agent uses only cleaned data; no PII in themes, quotes, or actions |
| Phase 8: Pulse Composition | Final report verified to be PII-free |
| Phase 9: Google Docs | Published document contains no PII |
| Phase 10: Gmail | Draft email contains no PII |
| Phase 11: Validation | Full end-to-end PII check |
