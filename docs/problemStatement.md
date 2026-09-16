# Problem Statement

## Overview

This milestone continues the same product selected in Milestone 1. The goal is to transform raw mobile-store feedback into a concise weekly pulse that a product team can scan within minutes.

The weekly pulse should help stakeholders understand:

- **What users care about most**
- **What users actually said**
- **What actions should be taken next**

Since App Store and Play Store reviews are already public, the system must aggregate, theme, summarize, and deliver insights through familiar tools such as Google Docs and Gmail. The solution should avoid custom credential handling or direct REST API wiring by using MCP-based integrations.

## End-to-End Flow

The completed system should be able to:

1. **Pull recent reviews** from the App Store and Play Store for the selected product.
2. **Cluster reviews into themes** to identify the most common user concerns.
3. **Generate a one-page weekly pulse** summarizing the key insights.
4. **Publish the note to Google Docs** so stakeholders can easily access it.
5. **Create a Gmail draft** containing the weekly note or a clear link to it.

## Deliverables

The weekly one-page pulse must include:

- **Top themes:** The most frequently discussed topics in user reviews.
- **Real user quotes:** Verbatim review snippets without invented wording.
- **Three action ideas:** Concrete next steps based on the identified themes.
- **Draft email:** A Gmail draft sent to yourself or an alias containing the note or a pointer to it.

## Target Audience

| Audience | Purpose |
|---|---|
| Product / Growth | Prioritize fixes and improvements using real user feedback. |
| Support | Align support messaging with what users are actually saying. |
| Leadership | Review a one-page product health check without reading raw reviews. |

## Functional Requirements

The system must:

- **Import reviews** from approximately the last 8–12 weeks.
- **Capture available review fields** such as rating, title, text, and date.
- **Group reviews into at most 5 themes**, such as onboarding, KYC, payments, statements, or withdrawals depending on the product.
- **Highlight the top 3 themes** in the weekly note.
- **Include 3 real user quotes** from the imported reviews.
- **Suggest 3 action ideas** based on the themes.
- **Draft an email** with the weekly note addressed to yourself or an alias.

## Integration Requirements

The solution must use MCP servers or MCP connectors for:

- **Google Docs:** To create or update the weekly pulse document.
- **Gmail:** To create the draft email message.

The integration approach must be MCP-first. The system should not use a custom OAuth client or direct Google REST API integration as the primary method for connecting to Google Docs or Gmail.

## Key Constraints

- **Reviews:** Use public review exports only. Do not scrape behind store logins or use automation that violates platform terms of service.
- **Themes:** Cluster reviews into a maximum of 5 themes.
- **Weekly pulse:** Highlight only the top 3 themes.
- **Length:** Keep the note scannable and within 250 words where applicable.
- **Privacy:** Do not include personally identifiable information such as usernames, emails, device IDs, or other reviewer identifiers. Quotes must be anonymous or stripped of identifying details.

## Expected Outcome

The expected outcome is a working system that converts public mobile-store reviews into a concise weekly product feedback report. The report should help stakeholders quickly understand user sentiment, identify recurring issues, and decide on practical next steps.

