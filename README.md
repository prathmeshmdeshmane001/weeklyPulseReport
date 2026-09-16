# Weekly Review Pulse Agent

## Overview

An AI agent that converts public App Store and Play Store reviews into a concise weekly product feedback pulse. The system analyzes recent reviews, groups them into themes, selects real user quotes, suggests action ideas, publishes the summary to Google Docs, and creates a Gmail draft — all through MCP-based integrations.

## Project Structure

```text
milestone 3/
│
├── phase1/                        # Requirement Understanding and Project Definition
│   ├── project_definition.md      # Project goals, scope, stakeholders, workflow
│   ├── review_input_schema.md     # Expected review data format and fields
│   ├── pulse_output_schema.md     # Weekly pulse report structure
│   ├── mcp_integration_plan.md    # Google Docs and Gmail MCP usage plan
│   └── privacy_rules.md           # PII handling and constraint rules
│
├── phase2/                        # Review Data Collection
├── phase3/                        # Data Normalization and Cleanup
├── phase4/                        # Privacy Protection and Safety Review
├── phase5/                        # AI Theme Analysis
├── phase6/                        # Theme Prioritization and Evidence Selection
├── phase7/                        # Action Idea Generation
├── phase8/                        # Weekly Pulse Composition
├── phase9/                        # Google Docs MCP Delivery
├── phase10/                       # Gmail MCP Draft Creation
├── phase11/                       # End-to-End Validation
├── phase12/                       # Final Documentation and Submission
│
├── docs/
│   ├── problemStatement.md        # Problem statement
│   ├── architecture.md            # System architecture
│   ├── implementationplan.md      # Phase-wise implementation plan
│   ├── eval.md                    # Phase-wise evaluation and exit criteria
│   └── decision.md                # Major technical and logical decisions
│
└── README.md                      # This file
```

## Phase Summary

| Phase | Folder | Purpose |
|-------|--------|---------|
| Phase 1 | `phase1/` | Requirement understanding, schemas, rules, MCP plan |
| Phase 2 | `phase2/` | Load and filter public review exports |
| Phase 3 | `phase3/` | Normalize fields across App Store and Play Store |
| Phase 4 | `phase4/` | Remove PII and filter low-quality reviews |
| Phase 5 | `phase5/` | AI agent clusters reviews into themes |
| Phase 6 | `phase6/` | Rank themes and select real user quotes |
| Phase 7 | `phase7/` | Generate action ideas from themes |
| Phase 8 | `phase8/` | Compose the concise weekly pulse |
| Phase 9 | `phase9/` | Publish pulse to Google Docs via MCP |
| Phase 10 | `phase10/` | Create Gmail draft via MCP |
| Phase 11 | `phase11/` | End-to-end validation and testing |
| Phase 12 | `phase12/` | Final documentation and submission |

## Key Constraints

- **Public review exports only** — no scraping or login-protected data.
- **Maximum 5 themes** — top 3 highlighted in the weekly pulse.
- **Real quotes only** — no invented or paraphrased user wording.
- **No PII** — all identifying information removed before output.
- **MCP-first** — Google Docs and Gmail accessed through MCP servers.
- **Concise output** — weekly pulse kept short and scannable.

## Current Status

- **Phase 1: Complete** — Project defined, schemas created, rules documented.
- **Phase 2–12: Pending** — Folders created with README placeholders.
