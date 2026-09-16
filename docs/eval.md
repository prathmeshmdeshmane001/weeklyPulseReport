# Evaluation Plan

## Overview

This document defines the testing approach, validation checks, and exit criteria for each implementation phase of the AI agent. The goal is to ensure that every phase is completed with clear evidence before moving to the next phase.

Each phase should be evaluated using:

- **Functional testing:** Confirms that the expected feature works.
- **Data validation:** Confirms that inputs and outputs are correct.
- **Privacy checks:** Confirms that no personally identifiable information is exposed.
- **MCP validation:** Confirms that Google Docs and Gmail operations use MCP tools.
- **Exit criteria:** Defines the minimum conditions required to consider the phase complete.

## Phase 1: Requirement Analysis and Setup

### Testing Approach

- Review the problem statement, architecture, and implementation plan for consistency.
- Confirm that the selected product and review source are clearly identified.
- Confirm that the expected review input format is documented.
- Confirm that Google Docs and Gmail MCP availability is known.

### Exit Criteria

- The project goal is clearly understood.
- Required input fields are identified.
- MCP-first integration requirement is confirmed.
- Initial project structure is agreed upon.

## Phase 2: Review Data Ingestion

### Testing Approach

- Test importing sample App Store and Play Store review exports.
- Verify that required fields such as rating, title, text, date, and platform are captured where available.
- Check that reviews outside the 8–12 week range are excluded.
- Validate that incomplete or invalid records are handled correctly.

### Exit Criteria

- Public review exports can be loaded successfully.
- Review records are normalized into a consistent format.
- Date filtering works as expected.
- Invalid or empty review entries are removed or ignored.

## Phase 3: Preprocessing and Privacy Protection

### Testing Approach

- Test text cleaning on sample review data.
- Check that emails, usernames, phone numbers, device IDs, and other PII are removed or masked.
- Verify that review quotes remain anonymous.
- Confirm that original quote wording is preserved after privacy cleanup.

### Exit Criteria

- Review text is cleaned and usable for analysis.
- No PII appears in processed data.
- Quotes remain faithful to the original review text.
- Data is safe to pass to the AI analysis agent.

## Phase 4: AI Agent Analysis

### Testing Approach

- Run the AI agent on a sample review dataset.
- Verify that reviews are grouped into no more than 5 themes.
- Confirm that the top 3 themes are selected from the generated theme set.
- Check that selected user quotes are real and traceable to source reviews.
- Validate that action ideas are based on actual themes.

### Exit Criteria

- Theme count does not exceed 5.
- Top 3 themes are identified clearly.
- 3 real user quotes are selected without invented wording.
- 3 action ideas are relevant and grounded in review themes.

## Phase 5: Weekly Pulse Generation

### Testing Approach

- Generate a weekly pulse from the AI analysis output.
- Check that the report includes title, date range, top themes, quotes, and action ideas.
- Verify that the report is concise and scannable.
- Confirm that the note stays within the expected word limit where applicable.

### Exit Criteria

- Weekly pulse includes all required sections.
- Report is readable by product, support, and leadership stakeholders.
- Output contains no fabricated quotes.
- Output contains no PII.

## Phase 6: Google Docs MCP Integration

### Testing Approach

- Test creating or updating a Google Docs document through the Google Docs MCP server.
- Confirm that the generated weekly pulse is inserted correctly.
- Verify formatting and readability in the document.
- Capture and validate the document link if available.

### Exit Criteria

- Google Docs operation is completed through MCP.
- Weekly pulse content appears correctly in the document.
- No custom Google Docs REST API integration is used as the primary path.
- Document link is available if required for email drafting.

## Phase 7: Gmail MCP Integration

### Testing Approach

- Test creating a Gmail draft through the Gmail MCP server.
- Confirm that the draft includes the weekly pulse or Google Docs link.
- Verify that the recipient is yourself or an approved alias.
- Check that the subject and body are clear and professional.

### Exit Criteria

- Gmail draft is created successfully through MCP.
- Draft contains the weekly pulse or a valid document link.
- Recipient is correct.
- No custom Gmail REST API integration is used as the primary path.

## Phase 8: End-to-End Validation

### Testing Approach

- Run the complete workflow from review import to Gmail draft creation.
- Validate each intermediate output.
- Confirm that all privacy, theme, quote, and length constraints are satisfied.
- Review the generated Google Docs document and Gmail draft manually.

### Exit Criteria

- End-to-end workflow completes successfully.
- Reviews are imported, cleaned, analyzed, summarized, and delivered.
- Google Docs and Gmail outputs are created using MCP.
- Final artifacts meet project requirements.

## Phase 9: Final Review and Submission

### Testing Approach

- Review all documentation files for completeness and consistency.
- Confirm that problem statement, architecture, implementation plan, evaluation plan, and decisions are aligned.
- Validate that known limitations and future enhancements are documented.
- Prepare final milestone submission materials.

### Exit Criteria

- Documentation is complete and submission-ready.
- All phase exit criteria are satisfied.
- Important decisions are recorded in the decision log.
- Final project package is ready for evaluation.
