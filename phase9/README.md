# Phase 9: Google Docs MCP Delivery

## Objective

Publish the weekly pulse to Google Docs using the MCP server.

## Prerequisites

Before running Phase 9, you need to:

1. **Create a Google Doc** in your Google Drive
   - Go to https://docs.google.com/document/create
   - This will be your weekly pulse document

2. **Get the Document ID** from the URL
   - Look at the URL: `https://docs.google.com/document/d/DOC_ID/edit`
   - Copy the long string between `/d/` and `/edit`

3. **Add to your `.env` file**:
   ```
   GDOCS_DOC_ID=your_doc_id_here
   ```

4. **Share the document** with the MCP service account if needed
   - The MCP server may use a service account to access your document

## How to Run

```bash
python phase9/publish_to_docs.py
```

## What It Does

1. Reads the weekly pulse JSON from `phase8/data/weekly_pulse/weekly_pulse.json`
2. Formats it as a readable document
3. Appends it to your Google Doc via MCP
4. Saves delivery status to `phase9/data/docs_delivery/phase9_delivery_status.json`

## Output

- **Google Doc**: Weekly pulse appended with timestamp
- **Status JSON**: `phase9/data/docs_delivery/phase9_delivery_status.json`
  - `success`: true/false
  - `document_id`: Your Google Doc ID
  - `document_url`: Link to the document
  - `timestamp`: When it was published

## MCP Server

- **URL**: https://saksham-mcp-server-production-7819.up.railway.app
- **Tool Used**: `append_to_doc`

## Files

- `publish_to_docs.py` - Main delivery script
- `data/docs_delivery/` - Output directory for delivery status
