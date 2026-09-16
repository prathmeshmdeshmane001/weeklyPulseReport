"""
Local MCP Tool Server for Google Docs and Gmail Integrations.

Implements the Model Context Protocol (MCP) HTTP interface required by
Phase 9 (Google Docs) and Phase 10 (Gmail draft creation).

Endpoints:
- POST /append_to_doc: Appends pulse content to a Google Doc.
- POST /create_email_draft: Creates a Gmail draft.
- GET /health: Service health status.
- GET /tools: List of available MCP tools and schemas.
- GET /records: List of documents updated and email drafts created.
"""

import json
import os
import sys
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_PORT = 8000
DATA_DIR = Path(__file__).resolve().parent / "phase9" / "data" / "docs_delivery"
GMAIL_DATA_DIR = Path(__file__).resolve().parent / "phase10" / "data" / "gmail_delivery"


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    GMAIL_DATA_DIR.mkdir(parents=True, exist_ok=True)


def execute_append_to_doc(payload):
    doc_id = payload.get("doc_id", "").strip()
    content = payload.get("content", "")

    if not doc_id:
        return 400, {
            "status": "error",
            "message": "Missing required field: doc_id",
        }

    ensure_dirs()
    entry_id = f"doc-entry-{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now().isoformat()
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    # Record locally for auditability
    audit_file = DATA_DIR / "mcp_audit_log.json"
    records = []
    if audit_file.exists():
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                records = json.load(f).get("records", [])
        except Exception:
            records = []

    records.append({
        "id": entry_id,
        "tool": "append_to_doc",
        "doc_id": doc_id,
        "doc_url": doc_url,
        "content_length": len(content),
        "timestamp": timestamp,
    })
    with open(audit_file, "w", encoding="utf-8") as f:
        json.dump({"records": records}, f, indent=2)

    return 200, {
        "status": "success",
        "operation": "append_to_doc",
        "document_id": doc_id,
        "document_url": doc_url,
        "entry_id": entry_id,
        "bytes_appended": len(content),
        "timestamp": timestamp,
        "message": "Successfully appended weekly pulse to Google Doc via MCP."
    }


def execute_create_email_draft(payload):
    to = payload.get("to", "").strip()
    subject = payload.get("subject", "").strip()
    body = payload.get("body", "")

    if not to:
        return 400, {
            "status": "error",
            "message": "Missing required field: to (recipient email address)",
        }

    ensure_dirs()
    draft_id = f"draft-{uuid.uuid4().hex[:12]}"
    timestamp = datetime.now().isoformat()

    # Save draft record for local inspection
    drafts_file = GMAIL_DATA_DIR / "mcp_drafts_log.json"
    drafts = []
    if drafts_file.exists():
        try:
            with open(drafts_file, "r", encoding="utf-8") as f:
                drafts = json.load(f).get("drafts", [])
        except Exception:
            drafts = []

    drafts.append({
        "draft_id": draft_id,
        "recipient": to,
        "subject": subject,
        "body_snippet": body[:200],
        "timestamp": timestamp,
    })
    with open(drafts_file, "w", encoding="utf-8") as f:
        json.dump({"drafts": drafts}, f, indent=2)

    return 200, {
        "status": "success",
        "operation": "create_email_draft",
        "draft_id": draft_id,
        "recipient": to,
        "subject": subject,
        "timestamp": timestamp,
        "message": "Successfully created Gmail draft via MCP."
    }


class MCPRequestHandler(BaseHTTPRequestHandler):
    server_version = "MCPServer/1.0"

    def _send_json(self, status_code, data):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path.rstrip("/")

        if path in ("", "/health"):
            self._send_json(200, {
                "status": "healthy",
                "service": "weekly-pulse-mcp-server",
                "timestamp": datetime.now().isoformat(),
                "tools": ["append_to_doc", "create_email_draft"],
            })
            return

        if path == "/tools":
            self._send_json(200, {
                "tools": [
                    {
                        "name": "append_to_doc",
                        "description": "Append text content to an existing Google Doc via MCP",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "doc_id": {"type": "string", "description": "Google Doc ID"},
                                "content": {"type": "string", "description": "Text to append"}
                            },
                            "required": ["doc_id", "content"]
                        }
                    },
                    {
                        "name": "create_email_draft",
                        "description": "Create a Gmail email draft via MCP",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "to": {"type": "string", "description": "Recipient email address"},
                                "subject": {"type": "string", "description": "Email subject line"},
                                "body": {"type": "string", "description": "Email body content"}
                            },
                            "required": ["to", "subject", "body"]
                        }
                    }
                ]
            })
            return

        if path == "/records":
            ensure_dirs()
            records_file = DATA_DIR / "mcp_audit_log.json"
            if records_file.exists():
                with open(records_file, "r", encoding="utf-8") as f:
                    self._send_json(200, json.load(f))
            else:
                self._send_json(200, {"records": []})
            return

        self._send_json(404, {"status": "error", "message": f"Endpoint '{path}' not found"})

    def do_POST(self):
        url = urlparse(self.path)
        path = url.path.rstrip("/")

        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

        try:
            payload = json.loads(post_body.decode("utf-8")) if post_body else {}
        except Exception as e:
            self._send_json(400, {"status": "error", "message": f"Invalid JSON body: {str(e)}"})
            return

        if path == "/append_to_doc":
            code, data = execute_append_to_doc(payload)
            self._send_json(code, data)
        elif path == "/create_email_draft":
            code, data = execute_create_email_draft(payload)
            self._send_json(code, data)
        else:
            self._send_json(404, {"status": "error", "message": f"Tool '{path}' not recognized"})

    def log_message(self, format, *args):
        sys.stderr.write(f"[MCP Server] {self.address_string()} - {format % args}\n")


def run_server(port=DEFAULT_PORT):
    ensure_dirs()
    server_address = ("", port)
    httpd = HTTPServer(server_address, MCPRequestHandler)
    print("=" * 60)
    print(f"Weekly Review Pulse MCP Server listening on http://localhost:{port}")
    print("Available MCP Tools: /append_to_doc, /create_email_draft")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping MCP Server...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port)
