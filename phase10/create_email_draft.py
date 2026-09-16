"""
Phase 10: Gmail MCP Draft Creation

Creates a Gmail draft containing the weekly pulse using the MCP server.
The draft can be reviewed and sent manually from Gmail.

Prerequisites:
1. Add EMAIL_RECIPIENT to your .env file with the recipient email address
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
            from mcp_server import execute_create_email_draft
            code, fallback_result = execute_create_email_draft(arguments)
            if code == 200:
                fallback_result["delivery_mode"] = "local_mcp_engine"
                return fallback_result
        except Exception:
            pass
        return {"error": str(exc)}


def create_email_draft(to, subject, body, server_url=None):
    """Create a Gmail draft using MCP."""
    if not to:
        return {"error": "Missing recipient email. Please set EMAIL_RECIPIENT in .env file."}
    
    result = call_mcp_tool("create_email_draft", {
        "to": to,
        "subject": subject,
        "body": body
    }, server_url=server_url)
    return result


def format_email_body(pulse_data, doc_url=None):
    """Format the weekly pulse into an email body."""
    headline = pulse_data.get("headline", "Weekly Review Pulse")
    top_themes = pulse_data.get("top_themes", [])
    quotes = pulse_data.get("quotes", [])
    actions = pulse_data.get("actions", [])
    
    lines = [
        "Hello,",
        "",
        "Here is the weekly app review pulse summary:",
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
        "KEY USER QUOTES",
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
    
    if doc_url:
        lines.extend([
            "=" * 50,
            "",
            "FULL REPORT",
            "",
            f"View the complete report in Google Docs: {doc_url}",
        ])
    
    lines.extend([
        "",
        "=" * 50,
        "",
        "This report was generated automatically from app store review analysis.",
        "",
        "Best regards,",
        "AI Review Analysis System",
    ])
    
    return "\n".join(lines)


def main():
    project_root = Path(__file__).resolve().parent.parent
    
    # Load environment variables
    load_env(project_root)
    
    pulse_json_path = project_root / "phase8" / "data" / "weekly_pulse" / "weekly_pulse.json"
    phase9_status_path = project_root / "phase9" / "data" / "docs_delivery" / "phase9_delivery_status.json"
    output_dir = project_root / "phase10" / "data" / "gmail_delivery"
    status_path = output_dir / "phase10_gmail_status.json"
    
    if not pulse_json_path.exists():
        raise FileNotFoundError(f"Weekly pulse not found: {pulse_json_path}")
    
    # Get email recipient from environment
    recipient = os.environ.get("EMAIL_RECIPIENT", "").strip()
    
    if not recipient:
        print("=" * 60)
        print("Phase 10: Gmail MCP Draft Creation")
        print("=" * 60)
        print("ERROR: EMAIL_RECIPIENT not found in environment")
        print()
        print("To fix this:")
        print("1. Add to .env file: EMAIL_RECIPIENT=your_email@example.com")
        print()
        save_json({
            "success": False,
            "error": "EMAIL_RECIPIENT not configured",
            "timestamp": datetime.now().isoformat(),
        }, str(status_path))
        sys.exit(1)
    
    pulse_data = load_json(str(pulse_json_path))
    
    # Get Google Doc URL from Phase 9 status if available
    doc_url = None
    if phase9_status_path.exists():
        phase9_status = load_json(str(phase9_status_path))
        if phase9_status.get("success"):
            doc_url = phase9_status.get("document_url")
    
    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"Weekly App Review Pulse - {today}"
    
    email_body = format_email_body(pulse_data, doc_url)
    
    mcp_url = get_mcp_server_url()
    print("=" * 60)
    print("Phase 10: Gmail MCP Draft Creation")
    print("=" * 60)
    print(f"Recipient: {recipient}")
    print(f"Subject: {subject}")
    print(f"MCP Server: {mcp_url}")
    print()
    
    result = create_email_draft(recipient, subject, email_body, server_url=mcp_url)
    
    if result.get("status") == "error" or "error" in result:
        error_msg = result.get("message") or result.get("error") or "Unknown error"
        status = {
            "success": False,
            "error": error_msg,
            "recipient": recipient,
            "subject": subject,
            "timestamp": datetime.now().isoformat(),
        }
        print(f"ERROR: {error_msg}")
        if "details" in result:
            print(f"Details: {result['details']}")
    else:
        status = {
            "success": True,
            "error": None,
            "recipient": recipient,
            "subject": subject,
            "doc_url": doc_url,
            "timestamp": datetime.now().isoformat(),
        }
        
        print("SUCCESS: Gmail draft created via MCP")
        print(f"Draft subject: {subject}")
        print()
        print("You can review and send the draft from your Gmail account.")
    
    save_json(status, str(status_path))
    print(f"\nDelivery status saved to: {status_path}")


if __name__ == "__main__":
    main()
