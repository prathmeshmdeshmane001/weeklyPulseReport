# Architecture

## Overview

This project is designed as an AI-agent-based workflow that converts public mobile app reviews into a weekly product feedback pulse. The system takes recent App Store and Play Store review exports, cleans and organizes the data, identifies repeated user concerns, generates a short weekly summary, publishes the summary to Google Docs, and prepares a Gmail draft for delivery.

The architecture follows an MCP-first approach. Google Docs and Gmail are not integrated through custom OAuth or direct REST API calls. Instead, the AI agent uses MCP servers or connectors to perform document and email actions. This keeps the project aligned with the required tooling and separates business logic from external service authentication.

## Architecture Goals

- **Create a repeatable weekly workflow:** The same process should work each week with a new review export.
- **Keep the system modular:** Review ingestion, privacy cleanup, AI analysis, report generation, and delivery are separate responsibilities.
- **Use AI for reasoning-heavy tasks:** Theme detection, summarization, quote selection, and action suggestion are handled by the AI agent.
- **Use MCP for tool execution:** Google Docs and Gmail actions are delegated to MCP tools.
- **Protect user privacy:** PII must be removed before content is used in final artifacts.
- **Produce stakeholder-ready output:** The final report must be short, readable, and useful for product, support, and leadership teams.

## High-Level System Flow

```text
Public Review Exports
        |
        v
Review Ingestion
        |
        v
Data Normalization
        |
        v
Privacy and Quality Filtering
        |
        v
AI Agent Analysis
        |
        +--> Theme Identification
        +--> Theme Ranking
        +--> Quote Selection
        +--> Action Idea Generation
        +--> Weekly Pulse Creation
        |
        v
MCP Tool Layer
        |
        +--> Google Docs MCP
        +--> Gmail MCP
        |
        v
Final Weekly Pulse and Email Draft
```

## Main Components

### 1. Review Data Source

The system starts with public review data from the App Store and Play Store. The preferred input is a public review export file, but the system may also use a public no-login review fetcher for public-facing store reviews when an export file is not available.

Expected review information may include:

- **Review text:** The actual feedback written by the user.
- **Review title:** A short heading if available.
- **Rating:** Star rating or numeric score.
- **Date:** When the review was posted.
- **Platform:** App Store or Play Store.
- **App version:** Optional, if available in the export.

This component must not use private store access, user credentials, or login-protected review data. Any public no-login fetcher must save retrieved reviews as raw input files before ingestion so the rest of the workflow remains auditable.

### 2. Review Ingestion

The ingestion component is responsible for bringing review data into the workflow. It reads exported or publicly fetched review data and prepares it for further processing.

The ingestion stage checks:

- **Whether review text exists**
- **Whether review dates are usable**
- **Whether the review belongs to the required time period**
- **Whether platform-specific fields need to be mapped into a common format**

The goal is to create one consistent review dataset regardless of whether reviews came from the App Store or Play Store.

### 3. Data Normalization

App Store and Play Store exports may use different field names or formats. The normalization step converts these differences into one common structure.

For example:

- **Different date formats** are converted into a consistent date representation.
- **Different rating formats** are normalized into one rating field.
- **Review title and body** are preserved separately when available.
- **Platform information** is added so analysis can compare sources if needed.

This step ensures the AI agent receives clean and predictable input.

### 4. Privacy and Quality Filtering

Before analysis, the review data must be checked for privacy and quality.

Privacy filtering removes or masks:

- **Email addresses**
- **Phone numbers**
- **Usernames**
- **Device identifiers**
- **Account numbers**
- **Any other personally identifiable details**

Quality filtering removes or ignores:

- **Blank reviews**
- **Duplicate reviews**
- **Reviews with unusable dates**
- **Reviews that do not contain meaningful feedback**

This component is important because the final Google Docs report and Gmail draft must not expose sensitive user information.

### 5. AI Analysis Agent

The AI agent is the central intelligence layer of the system. It receives cleaned review data and converts it into structured insights.

The current Phase 5-8 implementation is **API-free**. It does not call Groq, OpenAI, or any other external LLM provider. This avoids provider quota issues and keeps the workflow runnable during development and evaluation.

Groq with `llama-3.3-70b-versatile` may be added later as an optional enhancement, but it is not required for the current runnable pipeline. If Groq is enabled in the future, the known model limits are:

- **Requests per minute:** 30
- **Requests per day:** 1,000
- **Tokens per minute:** 12,000
- **Tokens per day:** 100,000

Because of these limits, any future LLM integration must be conservative with calls. The system must not send all available reviews directly to an LLM. Even if 2,000+ privacy-safe reviews are available, the active analysis working set should be capped to about 500 representative reviews for the current implementation.

The system performs a lightweight local analysis step. This analysis groups privacy-safe reviews using deterministic keyword and metadata signals, review counts, sentiment labels, and representative evidence snippets. This reduces noise, improves consistency, enforces the maximum-theme constraint, and avoids dependency on external API availability.

The local Phase 5 analysis prepares:

- **Candidate theme counts** based on repeated review topics.
- **Rating breakdown by theme** to show whether the theme is mostly negative, neutral, or positive.
- **Platform distribution** so App Store and Play Store signals can be compared.
- **Representative privacy-safe review snippets** for evidence.
- **Top recurring keywords** to identify dominant topics.

The 500-review working set should be selected locally using a representative sampling strategy instead of simple random selection. The sample should preserve important signals from the full privacy-safe dataset, including:

- **Theme coverage:** Include reviews from each candidate theme.
- **Sentiment balance:** Preserve positive, negative, and neutral review proportions where possible.
- **Recency:** Prefer recent reviews within the selected 8–12 week window.
- **Evidence quality:** Prefer reviews with enough detail to support theme explanation and quote selection.

The current API-free execution plan is:

- **Phase 5:** Locally identify candidate themes and produce up to 5 final themes.
- **Phase 6:** Locally rank themes and select 3 real privacy-safe quotes.
- **Phase 7:** Locally generate 3 action ideas from selected themes and evidence.
- **Phase 8:** Locally compose the final one-page weekly pulse.

This gives a normal run 0 external API calls. If an LLM enhancement is added later, it must remain optional and must preserve the same evidence rules.

The agent performs five major reasoning tasks:

- **Theme identification:** Finds repeated topics across reviews.
- **Theme grouping:** Groups similar reviews under a shared theme name.
- **Theme ranking:** Decides which themes appear most important or frequent.
- **Quote selection:** Selects real review snippets that support the themes.
- **Action recommendation:** Suggests practical next steps based on the feedback.

The agent must not invent user quotes. Any quote included in the weekly pulse must come from the source review data after privacy cleanup.

### 6. Weekly Pulse Generator

The weekly pulse generator turns the AI analysis output into a stakeholder-friendly document.

The pulse should include:

- **Report title**
- **Review date range**
- **Top 3 themes**
- **3 real user quotes**
- **3 action ideas**
- **Short conclusion or summary**

The report should be short enough to scan quickly. The purpose is not to create a long research report, but to provide a weekly product health signal.

### 7. MCP Integration Layer

The MCP integration layer is responsible for all external tool actions.

It connects the AI agent output to:

- **Google Docs MCP:** Creates or updates the weekly pulse document.
- **Gmail MCP:** Creates a draft email containing the summary or a link to the document.

This layer keeps external service operations separate from the core analysis workflow. Authentication, document creation, and email draft creation are handled through MCP tooling.

## Detailed Data Flow

1. **Review export is provided:** A public App Store or Play Store review export is used as input.
2. **Reviews are ingested:** The system reads the available review fields.
3. **Reviews are filtered by date:** Only reviews from the last 8–12 weeks are considered.
4. **Reviews are normalized:** Different platform formats are converted into one common structure.
5. **Privacy cleanup is applied:** PII and sensitive identifiers are removed.
6. **Low-quality entries are removed:** Empty, duplicate, or unusable reviews are excluded.
7. **AI agent analyzes the reviews:** The agent identifies and groups recurring issues.
8. **Themes are limited:** The system keeps a maximum of 5 themes.
9. **Top themes are selected:** The weekly pulse highlights the top 3 themes.
10. **Quotes are selected:** The agent selects 3 real, privacy-safe quotes.
11. **Actions are generated:** The agent proposes 3 concrete action ideas.
12. **Weekly pulse is created:** The final report is written in a concise format.
13. **Google Docs is updated:** The pulse is published through MCP.
14. **Gmail draft is created:** A draft email is prepared through MCP.

## Agent Boundaries

The AI agent should make decisions about meaning, grouping, summarization, and recommendation. It should not directly handle custom Google authentication or manually call Google REST APIs.

The agent is responsible for:

- **Understanding review meaning**
- **Grouping similar feedback**
- **Prioritizing themes**
- **Selecting valid quotes**
- **Writing the weekly pulse**
- **Using MCP tools for final delivery**

The agent is not responsible for:

- **Scraping private store pages**
- **Bypassing platform restrictions**
- **Creating custom Google API clients**
- **Including PII in final outputs**
- **Inventing review content**

## Output Artifacts

The system produces two main artifacts:

### Google Docs Weekly Pulse

This is the main stakeholder-facing report. It contains the weekly review summary, top themes, quotes, and action ideas.

### Gmail Draft

This is a ready-to-review email draft addressed to the user or an approved alias. It contains either the weekly note itself or a link to the Google Docs document.

## Automated Scheduling with GitHub Actions

The workflow can be automated using GitHub Actions for scheduled execution:

### Scheduler Component

GitHub Actions provides the scheduling infrastructure to run the complete pipeline automatically:

**Schedule Configuration:**
- **Cron Schedule**: Runs every Sunday at 9:00 AM UTC (`0 9 * * 0`)
- **Manual Trigger**: `workflow_dispatch` allows on-demand execution
- **Frequency**: Weekly execution aligns with the "weekly pulse" concept

**Workflow Steps:**
1. **Checkout**: Pulls latest code from repository
2. **Setup**: Installs Python 3.11 and dependencies
3. **Fetch Reviews**: Optionally fetches latest reviews (if API integration enabled)
4. **Execute Phases 3-10**: Runs the complete pipeline sequentially
5. **Validation**: Runs Phase 11 to verify outputs
6. **Commit Results**: Saves generated data back to repository
7. **Upload Artifacts**: Preserves outputs as downloadable artifacts

**Secrets Management:**
Sensitive configuration is stored in GitHub Secrets:
- `GROQ_API_KEY`: For AI analysis (Phases 5, 7, 8)
- `GDOCS_DOC_ID`: Target Google Doc ID for Phase 9
- `EMAIL_RECIPIENT`: Draft email recipient for Phase 10
- `GOOGLE_PLAY_API_KEY` (optional): For automated review fetching
- `APP_STORE_API_KEY` (optional): For automated review fetching

**Benefits:**
- **No local infrastructure needed**: Runs entirely on GitHub-hosted runners
- **Automatic weekly execution**: No manual intervention required
- **Version controlled**: Workflow definition is in `.github/workflows/`
- **Observable**: Execution logs visible in GitHub Actions tab
- **Reproducible**: Same environment every run

### Scheduler Architecture Flow

```text
GitHub Actions Scheduler (cron)
        |
        v
Repository Checkout
        |
        v
Environment Setup (Python, deps)
        |
        v
Phase 2-10 Execution (sequentially)
        |
        v
Phase 11 Validation
        |
        v
Commit Results to Repo
        |
        v
Upload Artifacts
```

## Key Constraints

- **Public data only:** Use public review exports only.
- **No scraping behind login:** Do not access protected store data.
- **Maximum 5 themes:** Theme clustering must remain focused.
- **Top 3 themes in report:** The final report should not overwhelm stakeholders.
- **Real quotes only:** Quotes must come from actual reviews.
- **No PII:** Final artifacts must not contain identifying user information.
- **MCP-first integrations:** Google Docs and Gmail must be accessed through MCP tools.
- **Concise report:** The weekly pulse should remain one-page and scannable.

## Architecture Summary

The architecture separates the project into a clear pipeline: review input, cleanup, AI analysis, report generation, and MCP-based delivery. This design keeps the system easy to understand, protects privacy, avoids unnecessary custom integrations, and produces a useful weekly feedback pulse for stakeholders.
