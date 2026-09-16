# Phase-Wise Implementation Plan

## Overview

This document explains how the AI agent for mobile review analysis will be implemented phase by phase. The plan focuses on what the system will do in each phase, what decisions must be made, what outputs are expected, and how each phase contributes to the final MCP-based workflow.

This plan does not describe coding details. It describes the logical implementation approach for building the complete review-to-weekly-pulse system.

## Phase 1: Requirement Understanding and Project Definition

### Objective

Understand the exact purpose of the project and define what the AI agent must produce.

### What We Are Doing

In this phase, we clarify the problem being solved. The project is not simply collecting reviews; it is converting raw public app reviews into a weekly business-friendly pulse. We define the selected product, the expected users of the report, the type of review data required, and the final output format.

We also confirm that the system must use MCP for Google Docs and Gmail instead of direct Google API integration. This phase creates a shared understanding of the project boundaries before implementation begins.

### Key Activities

- **Understand the product selected in Milestone 1**
- **Confirm that review data will come from public exports**
- **Identify the required review fields**
- **Define the weekly pulse structure**
- **Confirm the role of Google Docs and Gmail**
- **Confirm that MCP is the required integration method**
- **Identify privacy and reporting constraints**

### Expected Output

- Clear understanding of project goals.
- Defined input and output expectations.
- Confirmed MCP-first integration approach.
- Confirmed privacy and reporting rules.

## Phase 2: Review Data Collection Planning

### Objective

Plan how review data will be collected and prepared for the agent.

### What We Are Doing

In this phase, we define how public App Store and Play Store review data will be used. Since the project should not scrape private data or access store data behind login, the system depends on review export files, publicly available review datasets, or public no-login review fetchers for public-facing store reviews.

We decide which fields are important for analysis and how the review time range will be selected. The project requires reviews from approximately the last 8–12 weeks, so this phase defines how review dates will be used to filter the dataset.

### Key Activities

- **Identify available review export format**
- **Identify whether a public no-login fetcher is needed when an export is unavailable**
- **Check whether review data includes rating, title, text, date, and platform**
- **Decide how to handle missing optional fields**
- **Define the 8–12 week review window**
- **Separate useful reviews from incomplete entries**
- **Ensure only public review data is used**

### Expected Output

- Defined review data source.
- Raw review files produced from either export files or public no-login fetchers.
- Defined review time window.
- List of required and optional review fields.
- Clear rule for excluding incomplete or invalid reviews.

## Phase 3: Data Normalization and Cleanup

### Objective

Convert review data into a clean and consistent structure before analysis.

### What We Are Doing

App Store and Play Store data may not look exactly the same. One platform may provide a title while another may only provide review text. Dates and ratings may also appear in different formats. This phase focuses on making the data consistent so the AI agent can analyze it properly.

The system should treat all reviews in a standard way regardless of platform. This phase also removes entries that cannot support meaningful analysis, such as blank reviews or duplicate feedback.

### Key Activities

- **Map platform-specific fields into a common structure**
- **Standardize date values**
- **Standardize rating values**
- **Preserve review text and title where available**
- **Remove blank or duplicate reviews**
- **Prepare a clean review dataset for privacy filtering**

### Expected Output

- Normalized review dataset.
- Consistent review format across platforms.
- Removed duplicate, blank, or unusable records.

## Phase 4: Privacy Protection and Safety Review

### Objective

Ensure that no personally identifiable information appears in the final report or email draft.

### What We Are Doing

Before the AI agent analyzes the review content, the system must protect user privacy. Reviews may contain names, emails, phone numbers, account references, device identifiers, or other sensitive information. This phase defines how such information will be removed or masked.

The goal is to keep review feedback useful while making sure no private user details are passed into final stakeholder artifacts.

### Key Activities

- **Review the dataset for possible PII**
- **Remove or mask emails, phone numbers, usernames, and IDs**
- **Avoid including reviewer identity in quotes**
- **Keep the meaning of feedback intact after cleanup**
- **Confirm that selected quotes remain anonymous**

### Expected Output

- Privacy-safe review dataset.
- Clean review text ready for AI analysis.
- Confidence that final artifacts will not expose PII.

## Phase 5: AI Theme Analysis

### Objective

Use the AI agent to identify what users are talking about most.

### What We Are Doing

In this phase, the AI agent reads the cleaned reviews and groups similar feedback into themes. Themes represent repeated user concerns or praise, such as onboarding, payments, app crashes, login issues, withdrawals, statements, or customer support.

The system must not create too many themes. The project requires a maximum of 5 themes so the output remains focused and easy to understand.

The current implementation is **API-free**. It does not call Groq, OpenAI, or any other external API provider. This avoids provider quota failures and keeps the project runnable even when API providers are unavailable.

Groq with `llama-3.3-70b-versatile` may be added later as an optional enhancement. If enabled in the future, the known model limits are:

- **Requests per minute:** 30
- **Requests per day:** 1,000
- **Tokens per minute:** 12,000
- **Tokens per day:** 100,000

To stay provider-independent, the system does not send the privacy-safe dataset to any LLM in the current implementation. Even though the current dataset has around 2,400 privacy-safe reviews, the current implementation builds the analysis using a capped working set of about 500 representative reviews.

The system performs local analysis on the privacy-safe review dataset to produce candidate theme groups, review counts, rating breakdowns, platform distribution, recurring keywords, and representative review snippets. This keeps the output aligned with project constraints without depending on external API capacity.

The API-free analysis strategy is:

1. **Group reviews locally using deterministic signals** such as keywords for crashes, payments, KYC, withdrawals, support, and product experience.
2. **Count reviews per candidate theme** to measure frequency.
3. **Attach rating breakdowns** to distinguish urgent negative themes from positive product signals.
4. **Select a representative 500-review working set** from the privacy-safe dataset using theme coverage, sentiment balance, recency, and evidence quality.
5. **Attach source review IDs and compact privacy-safe snippets** so every theme remains evidence-based.
6. **Produce up to 5 final themes locally** without inventing evidence.

The Phase 5 API call budget is zero. The output is generated locally as structured JSON.

### Key Activities

- **Analyze review text for repeated topics**
- **Run local API-free analysis**
- **Cap the LLM working set to about 500 representative reviews**
- **Prepare candidate theme counts and evidence snippets**
- **Use deterministic local rules for theme refinement and concise summaries**
- **Group similar reviews under common theme names**
- **Limit the total number of themes to 5**
- **Identify how many reviews support each theme**
- **Separate major recurring themes from isolated comments**
- **Prepare theme summaries for report generation**

### Expected Output

- Up to 5 review themes.
- Short explanation of each theme.
- Review evidence supporting each theme.
- Local analysis report describing candidate themes and selected working set.
- API usage kept at zero calls.

## Phase 6: Theme Prioritization and Evidence Selection

### Objective

Select the most important themes and supporting quotes for the weekly pulse.

### What We Are Doing

After themes are created, the system decides which themes should appear in the final weekly pulse. The report should highlight only the top 3 themes because stakeholders need a short and focused summary.

This phase is handled locally. Theme ranking is calculated from review count, negative sentiment share, recency, and business relevance. Quote selection is handled locally by selecting privacy-safe snippets that are clear, representative, and linked to the selected themes.

The AI agent also selects 3 real user quotes. These quotes must be copied from actual reviews after privacy cleanup. The system must not invent or paraphrase fake quotes.

No external API call is required in Phase 6.

### Key Activities

- **Rank themes by frequency and importance**
- **Prefer local ranking to avoid unnecessary LLM calls**
- **Select the top 3 themes for the report**
- **Choose quotes that clearly represent user concerns**
- **Verify that each quote comes from source review data**
- **Check that quotes do not contain PII**
- **Connect quotes to the relevant themes**

### Expected Output

- Top 3 themes selected.
- 3 real user quotes selected.
- Evidence clearly linked to user feedback.
- Phase 6 completed with zero external API calls.

## Phase 7: Action Idea Generation

### Objective

Convert review insights into practical next steps.

### What We Are Doing

The weekly pulse should not only describe what users said. It should also suggest what the product team can do next. In this phase, the AI agent generates 3 action ideas based on the selected themes.

Action ideas should be concrete and grounded in the review evidence. They should help product, support, or growth teams decide what to investigate, fix, improve, or communicate.

This phase generates action ideas locally using theme-specific deterministic rules. It uses only the top 3 themes, their summaries, selected quotes, and key counts. It does not call any external API provider.

### Key Activities

- **Review top themes and supporting quotes**
- **Identify likely user pain points**
- **Suggest practical product or support actions**
- **Avoid vague recommendations**
- **Ensure action ideas are connected to actual review themes**
- **Generate action ideas locally without external API calls**

### Expected Output

- 3 action ideas.
- Each action idea connected to a theme.
- Recommendations suitable for stakeholder review.
- API usage limited to zero calls.

## Phase 8: Weekly Pulse Composition

### Objective

Create a concise one-page weekly note from the AI agent output.

### What We Are Doing

In this phase, the system combines the top themes, quotes, and action ideas into a polished weekly pulse. The note should be short, structured, and easy to scan.

This phase composes the final report locally using the selected inputs from Phases 5, 6, and 7. It does not send raw review data or selected evidence to any external API provider.

The report should be useful for product, growth, support, and leadership stakeholders. It should avoid unnecessary detail while still giving enough context to understand user sentiment and next steps.

### Key Activities

- **Create a clear title and date range**
- **Summarize the top 3 themes**
- **Include 3 real user quotes**
- **Add 3 action ideas**
- **Keep the note concise**
- **Check readability and structure**
- **Ensure no PII appears in the final text**
- **Compose the final report locally without external API calls**

### Expected Output

- Final weekly pulse draft.
- One-page stakeholder-ready summary.
- Concise report suitable for Google Docs and Gmail.
- API usage limited to zero calls.

### Phase 5-8 API Call Budget

The current call budget for one complete weekly analysis run is:

| Phase | External API Calls | Purpose |
|---|---:|---|
| Phase 5 | 0 | Locally identify up to 5 final themes |
| Phase 6 | 0 | Rank themes and select quotes locally |
| Phase 7 | 0 | Generate 3 grounded action ideas locally |
| Phase 8 | 0 | Compose the final weekly pulse locally |

The normal run uses 0 external API calls. This avoids provider quota failures entirely. A future Groq-based enhancement can be added later, but it must remain optional and must not block the API-free pipeline.

## Phase 9: Google Docs MCP Delivery

### Objective

Publish the weekly pulse to Google Docs using MCP.

### What We Are Doing

This phase uses the Google Docs MCP server or connector to create or update a document containing the weekly pulse. The project intentionally avoids direct Google Docs API integration because MCP is the required integration path.

The Google Docs document becomes the main place where stakeholders can read the weekly feedback pulse.

### Key Activities

- **Use the Google Docs MCP connector**
- **Create a new weekly pulse document or update an existing one**
- **Insert the final weekly report**
- **Check that formatting remains readable**
- **Collect the document link if available**

### Expected Output

- Google Docs document containing the weekly pulse.
- Optional document link for sharing through Gmail.
- Confirmation that Docs integration used MCP.

## Phase 10: Gmail MCP Draft Creation

### Objective

Create a Gmail draft that contains or links to the weekly pulse.

### What We Are Doing

After the weekly pulse is published to Google Docs, the system prepares a Gmail draft. The draft is addressed to the user or an approved alias. It may include the full weekly note or a link to the Google Docs document.

This phase completes the delivery workflow by preparing the communication that can be reviewed and sent.

### Key Activities

- **Use the Gmail MCP connector**
- **Prepare a clear email subject**
- **Add the weekly pulse or Docs link to the email body**
- **Set the recipient to self or approved alias**
- **Create the Gmail draft**
- **Review that the email is clear and professional**

### Expected Output

- Gmail draft ready for review.
- Email body containing the pulse or document link.
- Confirmation that Gmail integration used MCP.

## Phase 11: End-to-End Validation

### Objective

Verify that the full workflow works from review input to final Gmail draft.

### What We Are Doing

This phase checks whether all previous phases work together as one complete process. The goal is to confirm that the system can take review exports, clean them, analyze them, generate a weekly pulse, publish it to Google Docs, and create a Gmail draft.

Validation also checks that project constraints are satisfied, especially privacy, theme limits, real quote usage, and MCP-first integration.

### Key Activities

- **Run the complete workflow with sample review data**
- **Confirm only recent reviews are used**
- **Verify themes do not exceed 5**
- **Verify final report shows only top 3 themes**
- **Confirm quotes are real and privacy-safe**
- **Check the Google Docs output**
- **Check the Gmail draft output**
- **Review the final result from a stakeholder perspective**

### Expected Output

- End-to-end workflow validation.
- Verified weekly pulse.
- Verified Google Docs document.
- Verified Gmail draft.

## Phase 12: Final Documentation and Submission

### Objective

Prepare the project documentation and outputs for milestone submission.

### What We Are Doing

In the final phase, all documentation is reviewed for consistency. The problem statement, architecture, implementation plan, evaluation plan, and decision log should tell the same project story.

The submission should clearly show what the project does, how the AI agent works, why MCP is used, how privacy is handled, and how the final weekly pulse is delivered.

### Key Activities

- **Review all documentation files**
- **Confirm architecture matches implementation plan**
- **Confirm evaluation criteria match each phase**
- **Confirm major decisions are documented**
- **Prepare sample output if required**
- **List known limitations and future improvements**

### Expected Output

- Complete project documentation.
- Final milestone-ready submission package.
- Clear explanation of the AI agent and MCP workflow.

## Future Enhancements

### Implemented

- **Automated scheduling:** GitHub Actions workflow runs weekly every Sunday at 9:00 AM UTC. Includes manual trigger option and automated result committing.

### Planned

- **Sentiment analysis:** Show positive, neutral, and negative sentiment by theme.
- **Trend comparison:** Compare this week's themes with previous weeks.
- **Stakeholder dashboard:** Display review trends visually.
- **Multi-product support:** Run the same workflow for multiple apps.
- **More delivery channels:** Add Slack, Teams, or other stakeholder notification tools.
- **Live review fetching:** Automated daily fetching of new reviews via store APIs.
