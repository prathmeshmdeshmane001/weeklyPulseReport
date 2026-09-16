"""
Direct Google Docs Live Writer for Phase 9
Supports:
1. Google Apps Script Webhook (Zero GCP restrictions, works with organization-locked accounts)
2. Service Account Credentials (service_account.json)
3. OAuth 2.0 Client Credentials (credentials.json / token.json)
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


def find_credentials_path(project_root=None):
    root = Path(project_root or PROJECT_ROOT)
    candidates = [
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        root / "service_account.json",
        root / "google_credentials.json",
        root / "credentials.json",
        root / "client_secret.json",
        root / "phase9" / "service_account.json",
    ]
    for c in candidates:
        if c:
            p = Path(c)
            if p.exists() and p.is_file():
                return p
    return None

find_service_account_path = find_credentials_path


def append_via_webhook(webhook_url, content):
    """Appends content to Google Docs via a Google Apps Script Webhook."""
    if not webhook_url:
        return {"success": False, "error": "Missing webhook URL"}
    try:
        import requests
        resp = requests.post(
            webhook_url,
            json={"content": content},
            timeout=25
        )
        if resp.status_code in (200, 201):
            return {
                "success": True,
                "method": "apps_script_webhook",
                "status_code": resp.status_code,
                "characters_appended": len(content)
            }
        elif resp.status_code == 401:
            return {
                "success": False,
                "error": "permission_denied",
                "message": "Apps Script returned 401. In Apps Script > Deploy > Manage deployments > Edit, ensure 'Who has access' is set to 'Anyone'."
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {resp.status_code}",
                "message": f"Apps Script returned status {resp.status_code}: {resp.text[:200]}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": "webhook_call_failed",
            "message": f"Apps Script Webhook error: {str(e)}"
        }


def append_to_live_google_doc(doc_id, content, project_root=None):
    """Appends content directly to a Google Doc using Google Docs API or Webhook."""
    webhook_url = os.environ.get("GDOCS_WEBHOOK_URL", "").strip()
    if webhook_url:
        return append_via_webhook(webhook_url, content)

    cred_file = find_credentials_path(project_root)
    if not cred_file:
        return {
            "success": False,
            "error": "credentials_missing",
            "message": "No credentials or GDOCS_WEBHOOK_URL configured."
        }

    try:
        with open(cred_file, "r", encoding="utf-8") as f:
            cred_data = json.load(f)
    except Exception as e:
        return {"success": False, "error": f"Invalid credentials file: {e}"}

    try:
        from googleapiclient.discovery import build

        if cred_data.get("type") == "service_account":
            from google.oauth2 import service_account
            creds = service_account.Credentials.from_service_account_file(
                str(cred_file), scopes=SCOPES
            )
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request

            token_path = Path(project_root or PROJECT_ROOT) / "token.json"
            creds = None
            if token_path.exists():
                creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(str(cred_file), SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(token_path, "w", encoding="utf-8") as token_file:
                    token_file.write(creds.to_json())

        service = build("docs", "v1", credentials=creds)

        doc = service.documents().get(documentId=doc_id).execute()
        body_content = doc.get("body", {}).get("content", [])
        end_index = 1
        if body_content:
            end_index = max(1, body_content[-1].get("endIndex", 2) - 1)

        insert_text = f"\n\n{content}\n"
        requests_list = [
            {
                "insertText": {
                    "location": {"index": end_index},
                    "text": insert_text,
                }
            }
        ]

        service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests_list}
        ).execute()

        return {
            "success": True,
            "method": "google_docs_api_live",
            "document_id": doc_id,
            "document_url": f"https://docs.google.com/document/d/{doc_id}/edit",
            "characters_appended": len(insert_text),
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
