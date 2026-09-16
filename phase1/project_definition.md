# Project Definition

## Project Name

Weekly Review Pulse Agent

## Product Under Analysis

The product selected in Milestone 1. The same mobile application whose App Store and Play Store reviews will be analyzed throughout this project.

## Project Goal

Build an AI agent that reads public mobile app reviews, identifies recurring themes, selects real user quotes, generates actionable recommendations, and delivers a concise weekly feedback pulse through Google Docs and Gmail using MCP integrations.

## What the Agent Must Produce

Each week, the agent should produce:

1. **A weekly pulse report** containing:
   - Top 3 themes from user reviews
   - 3 real user quotes (verbatim, privacy-safe)
   - 3 action ideas grounded in the themes
2. **A Google Docs document** with the weekly pulse
3. **A Gmail draft** containing the pulse or a link to the document

## Stakeholders

| Audience | What They Get |
|----------|--------------|
| Product / Growth | Prioritized user signals for fixes and improvements |
| Support | Alignment between support messaging and real user concerns |
| Leadership | A one-page weekly health check on user sentiment |

## Data Source

- **App Store reviews** — public export
- **Play Store reviews** — public export
- **Time range:** Last 8–12 weeks of reviews
- **No scraping or login-protected access**

## Integration Method

- **Google Docs:** Accessed through MCP server or connector
- **Gmail:** Accessed through MCP server or connector
- **No custom OAuth or direct REST API integration**

## Constraints

- Maximum 5 themes for clustering
- Top 3 themes in the weekly pulse
- Real quotes only — no invented wording
- No PII in any output artifact
- Weekly pulse must be concise and scannable

## Expected Weekly Workflow

1. Import recent public review exports
2. Normalize and clean the review data
3. Remove PII and low-quality entries
4. AI agent clusters reviews into themes
5. Agent selects top themes, quotes, and action ideas
6. Agent composes the weekly pulse
7. Pulse published to Google Docs via MCP
8. Gmail draft created via MCP

## Success Criteria

- The system produces a useful weekly pulse from real review data
- Themes reflect actual user concerns
- Quotes are real and privacy-safe
- Action ideas are practical and grounded
- Google Docs and Gmail operations use MCP
- No PII appears in any final artifact
