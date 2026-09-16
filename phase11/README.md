# Phase 11: End-to-End Validation

## Objective

Verify that the full workflow works from review input to final Gmail draft.

## What It Does

This phase validates:
- All 10 phases produce expected outputs
- Project constraints are satisfied
- Privacy protection is working
- Theme limits are respected (max 5 themes)
- Top 3 themes are selected for report
- 3 real privacy-safe quotes are used
- 3 action ideas are generated
- MCP integration works (Google Docs and Gmail)

## How to Run

```bash
python phase11/validate_workflow.py
```

## Validations Performed

1. **Phase 3**: Data Normalization
   - Checks normalized reviews exist
   - Verifies required fields are present

2. **Phase 4**: Privacy Protection
   - Checks privacy-safe reviews exist
   - Scans sample for PII

3. **Phase 5**: Theme Analysis
   - Verifies max 5 themes constraint
   - Lists all identified themes

4. **Phase 6**: Theme Prioritization
   - Verifies exactly 3 top themes
   - Verifies exactly 3 quotes selected

5. **Phase 7**: Action Generation
   - Verifies exactly 3 actions generated

6. **Phase 8**: Weekly Pulse Composition
   - Verifies headline present
   - Verifies 3 themes, 3 quotes, 3 actions

7. **Phase 9**: Google Docs MCP Delivery
   - Verifies MCP call succeeded
   - Captures document URL

8. **Phase 10**: Gmail MCP Draft Creation
   - Verifies MCP call succeeded
   - Captures recipient and subject

## Output

- **Validation Report**: `phase11/data/validation/phase11_validation_report.json`
- **Console Report**: Color-coded status for each phase
- **Exit Code**: 0 if all passed, 1 if any failed

## Files

- `validate_workflow.py` - Main validation script
- `data/validation/` - Output directory for validation reports
