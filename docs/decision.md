# Decision Log

## Overview

This document records only the major technical and logical decisions made while designing the project. Minor formatting choices, wording changes, or small documentation edits are not included here.

The purpose of this file is to explain why the project is structured in a specific way and to make important design decisions easy to review later.

## Major Decisions

### DEC-001: Use an AI Agent as the Main Analysis Component

- **Category:** Technical / Logical
- **Status:** Accepted
- **Decision:** The system will be designed around an AI agent that performs review understanding, theme grouping, quote selection, action idea generation, and weekly pulse creation.
- **Reason:** The project requires interpretation of unstructured review text. An AI agent is suitable because it can understand meaning, group similar feedback, and produce stakeholder-friendly summaries.
- **Impact:** The core system becomes insight-focused rather than only data-processing-focused.

### DEC-002: Use MCP for Google Docs and Gmail Delivery

- **Category:** Technical / Integration
- **Status:** Accepted
- **Decision:** Google Docs and Gmail actions will be performed through MCP servers or connectors.
- **Reason:** The milestone requires an MCP-first integration approach. Using MCP avoids custom OAuth handling and direct Google REST API wiring.
- **Impact:** The project remains aligned with the required tooling and keeps external service operations separate from the main AI workflow.

### DEC-003: Use Public Review Exports or Public No-Login Fetchers as the Data Source

- **Category:** Technical / Business / Privacy
- **Status:** Accepted
- **Decision:** The system will use public App Store and Play Store review exports as the preferred input. If an export is unavailable, the system may use a public no-login review fetcher for public-facing store reviews.
- **Reason:** Public exports remain the safest option, but public no-login fetchers allow the system to satisfy the requirement to pull recent public reviews without using private credentials or login-protected store data.
- **Impact:** The project can process real public reviews while keeping the data source transparent. Any fetched reviews must be saved as raw input files before ingestion for auditability.

### DEC-004: Keep Review Processing Modular

- **Category:** Technical / Architecture
- **Status:** Accepted
- **Decision:** The architecture separates review ingestion, normalization, privacy filtering, AI analysis, report generation, and MCP delivery into distinct stages.
- **Reason:** A modular workflow is easier to understand, test, explain, and improve phase by phase.
- **Impact:** Each part of the system has a clear responsibility, which supports better evaluation and future enhancement.

### DEC-005: Apply Privacy Filtering Before AI Analysis and Final Output

- **Category:** Technical / Privacy
- **Status:** Accepted
- **Decision:** Reviews must be cleaned for personally identifiable information before being used in final reports or delivery artifacts.
- **Reason:** User reviews may contain emails, names, phone numbers, account references, or device identifiers. These should not appear in Google Docs or Gmail outputs.
- **Impact:** The generated weekly pulse is safer to share with stakeholders.

### DEC-006: Limit Themes to a Maximum of 5 and Report Only the Top 3

- **Category:** Logical / Product
- **Status:** Accepted
- **Decision:** The agent will group reviews into at most 5 themes and include only the top 3 themes in the weekly pulse.
- **Reason:** Too many themes would make the report difficult to scan. A limited set keeps the pulse focused and useful for stakeholders.
- **Impact:** The final output remains concise while still representing the most important user feedback.

### DEC-007: Use Only Real User Quotes

- **Category:** Logical / Product
- **Status:** Accepted
- **Decision:** Quotes in the weekly pulse must be real snippets from the review data after privacy cleanup.
- **Reason:** Generated or invented quotes would reduce trust and misrepresent user feedback.
- **Impact:** The report remains evidence-based and credible.

### DEC-008: Generate Action Ideas from Review Themes

- **Category:** Logical / Product
- **Status:** Accepted
- **Decision:** The weekly pulse will include 3 action ideas based on the selected themes.
- **Reason:** Stakeholders need practical next steps, not only a summary of user complaints or praise.
- **Impact:** The output becomes more useful for product, support, and growth planning.

### DEC-009: Keep the Final Pulse Short and Stakeholder-Friendly

- **Category:** Logical / Product
- **Status:** Accepted
- **Decision:** The weekly pulse will be concise, scannable, and suitable for a one-page Google Docs report.
- **Reason:** Product, support, and leadership teams need quick insight without reading large volumes of raw reviews.
- **Impact:** The report is more likely to be read and used regularly.

## Decisions Not Included

The following are intentionally not tracked in this file:

- **Small wording changes in documentation**
- **Markdown formatting choices**
- **Temporary implementation details**
- **Low-impact file organization choices**

Only major technical or logical decisions that affect project direction should be added here.
