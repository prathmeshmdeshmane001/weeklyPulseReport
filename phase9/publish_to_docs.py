"""
Phase 9: Google Docs MCP Delivery

Publishes the weekly pulse to Google Docs using the MCP server.
Appends the weekly pulse to an existing Google Doc.

Prerequisites:
1. Create a Google Doc manually in your Google Drive
2. Copy the document ID from the URL (the long string between /d/ and /edit)
3. Add GDOCS_DOC_ID to your .env file
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime


DEFAULT_MCP_SERVER_URL = "http://localhost:8000"

# Load .env file manually for compatibility
def load_env(project_root):
    env_path = Path(project_root) / ".env"
    if not env_path.exists():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")


def get_mcp_server_url():
    return os.environ.get("MCP_SERVER_URL", DEFAULT_MCP_SERVER_URL).rstrip("/")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def call_mcp_tool(tool_name, arguments, server_url=None):
    """Call an MCP tool via HTTP POST, with direct local MCP fallback."""
    base_url = (server_url or get_mcp_server_url()).rstrip("/")
    url = f"{base_url}/{tool_name}"
    body = arguments
    data = json.dumps(body).encode("utf-8")
    
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        # Fallback to local MCP server engine if running locally or in isolated sandbox
        try:
            project_root = Path(__file__).resolve().parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            from mcp_server import execute_append_to_doc
            code, fallback_result = execute_append_to_doc(arguments)
            if code == 200:
                fallback_result["delivery_mode"] = "local_mcp_engine"
                return fallback_result
        except Exception:
            pass
        return {"error": str(exc)}


def append_to_document(doc_id, content, server_url=None):
    """Append content to an existing Google Doc using MCP."""
    if not doc_id:
        return {"error": "Missing GDOCS_DOC_ID. Please set it in .env file."}
    
    result = call_mcp_tool("append_to_doc", {
        "doc_id": doc_id,
        "content": content
    }, server_url=server_url)
    return result


def format_pulse_for_docs(pulse_data):
    """Format the weekly pulse data into a readable document format."""
    headline = pulse_data.get("headline", "Weekly Review Pulse")
    top_themes = pulse_data.get("top_themes", [])
    quotes = pulse_data.get("quotes", [])
    actions = pulse_data.get("actions", [])
    
    lines = [
        "WEEKLY APP REVIEW PULSE",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "=" * 50,
        "",
        "HEADLINE",
        "",
        headline,
        "",
        "=" * 50,
        "",
        "TOP THEMES",
        "",
    ]
    
    for i, theme in enumerate(top_themes, 1):
        label = theme.get("label", f"Theme {i}")
        description = theme.get("description", "")
        lines.append(f"{i}. {label}")
        if description:
            lines.append(f"   {description}")
        lines.append("")
    
    lines.extend([
        "=" * 50,
        "",
        "REAL USER QUOTES",
        "",
    ])
    
    for i, quote in enumerate(quotes, 1):
        lines.append(f'{i}. "{quote}"')
        lines.append("")
    
    lines.extend([
        "=" * 50,
        "",
        "RECOMMENDED ACTIONS",
        "",
    ])
    
    for i, action in enumerate(actions, 1):
        lines.append(f"{i}. {action}")
        lines.append("")
    
    lines.extend([
        "=" * 50,
        "",
        "This report was generated automatically from app store review analysis.",
    ])
    
    return "\n".join(lines)


def main():
    project_root = Path(__file__).resolve().parent.parent
    
    # Load environment variables
    load_env(project_root)
    
    pulse_json_path = project_root / "phase8" / "data" / "weekly_pulse" / "weekly_pulse.json"
    output_dir = project_root / "phase9" / "data" / "docs_delivery"
    status_path = output_dir / "phase9_delivery_status.json"
    
    if not pulse_json_path.exists():
        raise FileNotFoundError(f"Weekly pulse not found: {pulse_json_path}")
    
    # Get document ID from environment
    doc_id = os.environ.get("GDOCS_DOC_ID", "").strip()
    if "/d/" in doc_id:
        doc_id = doc_id.split("/d/")[1].split("/")[0]
    
    if not doc_id:
        print("=" * 60)
        print("Phase 9: Google Docs MCP Delivery")
        print("=" * 60)
        print("ERROR: GDOCS_DOC_ID not found in environment")
        print()
        print("To fix this:")
        print("1. Create a Google Doc in your Google Drive")
        print("2. Copy the document ID from the URL")
        print("   (e.g., from https://docs.google.com/document/d/DOC_ID/edit)")
        print("3. Add to .env file: GDOCS_DOC_ID=your_doc_id_here")
        print()
        save_json({
            "success": False,
            "error": "GDOCS_DOC_ID not configured",
            "timestamp": datetime.now().isoformat(),
        }, str(status_path))
        sys.exit(1)
    
    pulse_data = load_json(str(pulse_json_path))
    formatted_content = format_pulse_for_docs(pulse_data)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    mcp_url = get_mcp_server_url()
    print("=" * 60)
    print("Phase 9: Google Docs MCP Delivery")
    print("=" * 60)
    print(f"Document ID: {doc_id}")
    print(f"MCP Server: {mcp_url}")
    print(f"Pulse date: {today}")
    print()
    
    result = append_to_document(doc_id, formatted_content, server_url=mcp_url)
    
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    
    if result.get("status") == "error" or "error" in result:
        error_msg = result.get("message") or result.get("error") or "Unknown error"
        status = {
            "success": False,
            "error": error_msg,
            "document_id": doc_id,
            "document_url": doc_url,
            "timestamp": datetime.now().isoformat(),
        }
        print(f"ERROR: {error_msg}")
        if "details" in result:
            print(f"Details: {result['details']}")
    else:
        status = {
            "success": True,
            "error": None,
            "document_id": doc_id,
            "document_url": doc_url,
            "pulse_date": today,
            "timestamp": datetime.now().isoformat(),
        }
        
        print("SUCCESS: Weekly pulse appended to Google Doc via MCP")
        print(f"Document URL: {doc_url}")

    # Direct live Google Docs API integration if service account credentials exist
    try:
        if str(project_root / "phase9") not in sys.path:
            sys.path.insert(0, str(project_root / "phase9"))
        from google_docs_writer import append_to_live_google_doc, find_service_account_path
        
        webhook_url = os.environ.get("GDOCS_WEBHOOK_URL", "").strip()
        service_cred = find_service_account_path(project_root)
        
        if webhook_url:
            print("\n🚀 Appending directly to live Google Doc via Apps Script Webhook...")
            live_res = append_to_live_google_doc(doc_id, formatted_content, project_root)
            if live_res.get("success"):
                print(f"✅ LIVE GOOGLE DOCS API: Successfully appended {live_res.get('characters_appended')} characters directly to your Google Doc!")
                status["live_google_api_success"] = True
            else:
                print(f"⚠ Live Google Docs Webhook returned: {live_res.get('message')}")
                status["live_google_api_error"] = live_res.get("message")
        elif service_cred:
            print(f"\n🔑 Found Google credentials: {service_cred.name}")
            print("🚀 Appending directly to live Google Doc via Google Docs API v1...")
            live_res = append_to_live_google_doc(doc_id, formatted_content, project_root)
            if live_res.get("success"):
                print(f"✅ LIVE GOOGLE DOCS API: Successfully appended {live_res.get('characters_appended')} characters directly to your Google Doc!")
                status["live_google_api_success"] = True
                status["service_account"] = live_res.get("service_account_used")
            else:
                print(f"⚠ Live Google Docs API call returned: {live_res.get('message')}")
                status["live_google_api_error"] = live_res.get("message")
        else:
            print("\nℹ Live Google Docs Direct Writing:")
            print("  To have Python directly insert text into your live Google Doc:")
            print("  Option A: Set GDOCS_WEBHOOK_URL in .env (Google Apps Script Webhook).")
            print("  Option B: Save Google Service Account JSON as 'service_account.json' in this project root.")
    except Exception as e:
        print(f"Notice: Direct Google Docs writer check: {e}")
    
    save_json(status, str(status_path))
    print(f"\nDelivery status saved to: {status_path}")


if __name__ == "__main__":
    main()
