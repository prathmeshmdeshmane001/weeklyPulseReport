"""
Unified Web, API & MCP Server for Weekly Review Pulse Report

Features:
1. MCP Tool Endpoints (/append_to_doc, /create_email_draft, /health, /tools)
2. JSON REST APIs (/api/pulse, /api/reviews, /api/status, /api/validation)
3. Static Web Serving for Dashboard & Frontend
"""

import json
import mimetypes
import os
import subprocess
import sys
import threading
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_PORT = int(os.environ.get("PORT", 8000))

# Import MCP handlers from mcp_server
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp_server import execute_append_to_doc, execute_create_email_draft, ensure_dirs


class UnifiedServerHandler(SimpleHTTPRequestHandler):
    server_version = "WeeklyPulseServer/2.0"

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

    def _serve_file(self, file_path):
        p = Path(file_path)
        if not p.exists() or not p.is_file():
            self._send_json(404, {"error": f"File '{p.name}' not found"})
            return
        mime_type, _ = mimetypes.guess_type(str(p))
        mime_type = mime_type or "application/octet-stream"
        with open(p, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path.rstrip("/")

        # Root redirect
        if path == "" or path == "/":
            build_index = PROJECT_ROOT / "frontend" / "build" / "index.html"
            if build_index.exists():
                self._serve_file(build_index)
                return
            dashboard_index = PROJECT_ROOT / "dashboard" / "index.html"
            if dashboard_index.exists():
                self._serve_file(dashboard_index)
                return
            self._send_json(200, {
                "message": "Weekly Review Pulse Server Active",
                "endpoints": ["/api/pulse", "/api/reviews", "/dashboard/index.html", "/health"]
            })
            return

        # MCP Health & Tools
        if path == "/health":
            self._send_json(200, {
                "status": "healthy",
                "service": "weekly-pulse-unified-server",
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
                                "doc_id": {"type": "string"},
                                "content": {"type": "string"}
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
                                "to": {"type": "string"},
                                "subject": {"type": "string"},
                                "body": {"type": "string"}
                            },
                            "required": ["to", "subject", "body"]
                        }
                    }
                ]
            })
            return

        # REST APIs for frontend
        if path == "/api/pulse":
            f = PROJECT_ROOT / "phase8" / "data" / "weekly_pulse" / "weekly_pulse.json"
            self._serve_file(f)
            return

        if path == "/api/reviews":
            f = PROJECT_ROOT / "phase4" / "data" / "privacy_safe" / "privacy_safe_reviews.json"
            self._serve_file(f)
            return

        if path == "/api/validation":
            f = PROJECT_ROOT / "phase11" / "data" / "validation" / "phase11_validation_report.json"
            self._serve_file(f)
            return

        if path == "/api/docs-status":
            f = PROJECT_ROOT / "phase9" / "data" / "docs_delivery" / "phase9_delivery_status.json"
            self._serve_file(f)
            return

        if path == "/api/gmail-status":
            f = PROJECT_ROOT / "phase10" / "data" / "gmail_delivery" / "phase10_gmail_status.json"
            self._serve_file(f)
            return

        if path == "/api/submission":
            f = PROJECT_ROOT / "phase12" / "data" / "submission" / "phase12_submission_summary.json"
            self._serve_file(f)
            return

        # Serve static dashboard files
        if path.startswith("/dashboard"):
            rel_file = path[len("/dashboard"):].lstrip("/") or "index.html"
            target = PROJECT_ROOT / "dashboard" / rel_file
            if target.exists():
                self._serve_file(target)
                return

        # Serve static public data files
        if path.startswith("/data"):
            rel_file = path[len("/data"):].lstrip("/")
            target = PROJECT_ROOT / "frontend" / "public" / "data" / rel_file
            if target.exists():
                self._serve_file(target)
                return

        # Serve frontend build if exists
        build_dir = PROJECT_ROOT / "frontend" / "build"
        if build_dir.exists():
            candidate = build_dir / path.lstrip("/")
            if candidate.exists() and candidate.is_file():
                self._serve_file(candidate)
                return
            index_file = build_dir / "index.html"
            if index_file.exists():
                self._serve_file(index_file)
                return

        self._send_json(404, {"error": f"Path '{path}' not found"})

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

        # MCP Tools
        if path == "/append_to_doc":
            code, data = execute_append_to_doc(payload)
            self._send_json(code, data)
            return

        if path == "/create_email_draft":
            code, data = execute_create_email_draft(payload)
            self._send_json(code, data)
            return

        if path == "/api/run-pipeline":
            def run_async():
                subprocess.run([sys.executable, str(PROJECT_ROOT / "run_pipeline.py")], cwd=str(PROJECT_ROOT))
            threading.Thread(target=run_async, daemon=True).start()
            self._send_json(202, {"status": "accepted", "message": "Pipeline run started in background"})
            return

        self._send_json(404, {"status": "error", "message": f"Tool or endpoint '{path}' not found"})


def run(port=DEFAULT_PORT):
    ensure_dirs()
    server_address = ("", port)
    httpd = HTTPServer(server_address, UnifiedServerHandler)
    print("=" * 65)
    print(f"Weekly Review Pulse Unified Server running on http://localhost:{port}")
    print(f"  • Standalone Dashboard: http://localhost:{port}/dashboard/index.html")
    print(f"  • MCP Tools:            http://localhost:{port}/append_to_doc, /create_email_draft")
    print(f"  • REST APIs:            http://localhost:{port}/api/pulse, /api/reviews")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    port = DEFAULT_PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run(port)
