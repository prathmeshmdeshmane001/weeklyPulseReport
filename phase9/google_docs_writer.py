"""
Direct Google Docs API Integration for Phase 9
Appends report text directly to a live Google Doc using Service Account credentials.
"""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]


def find_service_account_path(project_root=None):
    root = Path(project_root or PROJECT_ROOT)
    candidates = [
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        root / "service_account.json",
        root / "google_credentials.json",
        root / "credentials.json",
        root / "phase9" / "service_account.json",
    ]
    for c in candidates:
        if c:
            p = Path(c)
            if p.exists() and p.is_file():
                return p
    return None


def append_to_live_google_doc(doc_id, content, project_root=None):
    """
    Appends content directly to a Google Doc using Google Docs API v1.
    Requires service_account.json in the project root.
    """
    cred_file = find_service_account_path(project_root)
    if not cred_file:
        return {
            "success": False,
            "error": "service_account_missing",
            "message": "service_account.json not found in project root. Place your Google Cloud service account JSON in the project root and share the doc with the service account email."
        }

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as e:
        return {
            "success": False,
            "error": "missing_libraries",
            "message": f"Google API libraries not installed: {str(e)}"
        }

    try:
        creds = service_account.Credentials.from_service_account_file(
            str(cred_file), scopes=SCOPES
        )
        service = build("docs", "v1", credentials=creds)

        # Get document to find current end index
        doc = service.documents().get(documentId=doc_id).execute()
        body_content = doc.get("body", {}).get("content", [])
        
        # Calculate insert location (just before the final newline)
        end_index = 1
        if body_content:
            end_index = max(1, body_content[-1].get("endIndex", 2) - 1)

        insert_text = f"\n\n{content}\n"
        requests = [
            {
                "insertText": {
                    "location": {"index": end_index},
                    "text": insert_text,
                }
            }
        ]

        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute()

        return {
            "success": True,
            "method": "google_docs_api_live",
            "document_id": doc_id,
            "document_url": f"https://docs.google.com/document/d/{doc_id}/edit",
            "updated_index": end_index,
            "characters_appended": len(insert_text),
            "service_account_used": creds.service_account_email
        }
    except Exception as err:
        return {
            "success": False,
            "error": "api_call_failed",
            "message": f"Google Docs API error: {str(err)}"
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 google_docs_writer.py <DOC_ID> [CONTENT]")
        sys.exit(1)
    doc_id = sys.argv[1]
    content = sys.argv[2] if len(sys.argv) > 2 else "Test entry from Weekly Review Pulse."
    res = append_to_live_google_doc(doc_id, content)
    print(json.dumps(res, indent=2))
