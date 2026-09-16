# Tests

## Overview

This folder contains all unit, integration, and end-to-end validation tests for the project.

## Structure

Tests will be organized by phase:

```text
tests/
├── test_phase2_ingestion/       # Review data loading and filtering tests
├── test_phase3_normalization/   # Field mapping and standardization tests
├── test_phase4_privacy/         # PII detection and removal tests
├── test_phase5_analysis/        # Theme clustering tests
├── test_phase6_prioritization/  # Theme ranking and quote selection tests
├── test_phase7_actions/         # Action idea generation tests
├── test_phase8_pulse/           # Weekly pulse composition tests
├── test_phase9_docs_mcp/        # Google Docs MCP integration tests
├── test_phase10_gmail_mcp/      # Gmail MCP integration tests
└── test_phase11_e2e/            # Full end-to-end workflow validation
```

## Status

Pending — test files will be added as each phase is implemented.
