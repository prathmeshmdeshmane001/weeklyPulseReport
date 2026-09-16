"""
Unit tests for the Unified Web & MCP Server (server.py)
Tests server handlers in-process without requiring external network sockets.
"""

import json
import os
import sys
import unittest
from io import BytesIO
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server import UnifiedServerHandler


class InProcessHandler(UnifiedServerHandler):
    """Subclass of UnifiedServerHandler to test HTTP endpoints in-process."""
    def __init__(self, method, path, body_data=None):
        self.command = method
        self.path = path
        body_bytes = json.dumps(body_data).encode("utf-8") if isinstance(body_data, dict) else (body_data or b"")
        self.rfile = BytesIO(body_bytes)
        self.wfile = BytesIO()
        self.headers = {"Content-Length": str(len(body_bytes))}
        self.status_code = 200
        self.sent_headers = {}

        if method == "GET":
            self.do_GET()
        elif method == "POST":
            self.do_POST()
        elif method == "OPTIONS":
            self.do_OPTIONS()

    def send_response(self, code, message=None):
        self.status_code = code

    def send_header(self, keyword, value):
        self.sent_headers[keyword.lower()] = value

    def end_headers(self):
        pass

    def get_json(self):
        self.wfile.seek(0)
        return json.loads(self.wfile.read().decode("utf-8"))

    def get_body(self):
        self.wfile.seek(0)
        return self.wfile.read()


class TestUnifiedServer(unittest.TestCase):
    def test_health_check(self):
        handler = InProcessHandler("GET", "/health")
        self.assertEqual(handler.status_code, 200)
        data = handler.get_json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertIn("tools", data)

    def test_tools_discovery(self):
        handler = InProcessHandler("GET", "/tools")
        self.assertEqual(handler.status_code, 200)
        data = handler.get_json()
        tool_names = [t["name"] for t in data.get("tools", [])]
        self.assertIn("append_to_doc", tool_names)
        self.assertIn("create_email_draft", tool_names)

    def test_api_pulse(self):
        handler = InProcessHandler("GET", "/api/pulse")
        self.assertEqual(handler.status_code, 200)
        data = handler.get_json()
        self.assertIn("top_themes", data)

    def test_api_reviews(self):
        handler = InProcessHandler("GET", "/api/reviews")
        self.assertEqual(handler.status_code, 200)
        data = handler.get_json()
        self.assertIsInstance(data, list)

    def test_api_validation(self):
        handler = InProcessHandler("GET", "/api/validation")
        self.assertEqual(handler.status_code, 200)
        data = handler.get_json()
        self.assertTrue(data.get("overall_valid", False))

    def test_mcp_append_to_doc(self):
        handler = InProcessHandler("POST", "/append_to_doc", {
            "doc_id": "test_doc_id",
            "content": "# Test Header\nTest content."
        })
        self.assertEqual(handler.status_code, 200)
        data = handler.get_json()
        self.assertEqual(data.get("status"), "success")

    def test_mcp_create_email_draft(self):
        handler = InProcessHandler("POST", "/create_email_draft", {
            "to": "test@example.com",
            "subject": "Test Weekly Report",
            "body": "Hello Support Team"
        })
        self.assertEqual(handler.status_code, 200)
        data = handler.get_json()
        self.assertEqual(data.get("status"), "success")

    def test_dashboard_static(self):
        handler = InProcessHandler("GET", "/dashboard/index.html")
        self.assertEqual(handler.status_code, 200)
        self.assertIn(b"Groww", handler.get_body())

    def test_root_serves_html(self):
        handler = InProcessHandler("GET", "/")
        self.assertEqual(handler.status_code, 200)
        self.assertIn(b"<html", handler.get_body().lower())

    def test_options_cors(self):
        handler = InProcessHandler("OPTIONS", "/api/pulse")
        self.assertEqual(handler.status_code, 204)


if __name__ == "__main__":
    unittest.main()
