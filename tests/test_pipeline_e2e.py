"""
End-to-End Integration Tests for Weekly Review Pulse Pipeline

Tests:
1. MCP Server functionality (/health, /tools, /append_to_doc, /create_email_draft)
2. Phase 9 & 10 MCP integration scripts
3. Phase 11 validation report and all 7 project constraints
4. Phase 12 submission summary
"""

import json
import os
import subprocess
import sys
import time
import unittest
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestPipelineE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure .env exists
        env_file = PROJECT_ROOT / ".env"
        if not env_file.exists():
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("MCP_SERVER_URL=http://localhost:8899\n")
                f.write("GDOCS_DOC_ID=test-doc-id-123\n")
                f.write("EMAIL_RECIPIENT=test@example.com\n")

        os.environ["MCP_SERVER_URL"] = "http://localhost:8899"
        os.environ["GDOCS_DOC_ID"] = "test-doc-id-123"
        os.environ["EMAIL_RECIPIENT"] = "test@example.com"

        # Start local MCP server on port 8899 for testing
        cls.mcp_proc = subprocess.Popen(
            [sys.executable, str(PROJECT_ROOT / "mcp_server.py"), "8899"],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Wait for server to bind
        time.sleep(1.0)

    @classmethod
    def tearDownClass(cls):
        if cls.mcp_proc:
            try:
                cls.mcp_proc.terminate()
            except Exception:
                pass

    def test_01_mcp_tools_registration(self):
        from mcp_server import execute_append_to_doc, execute_create_email_draft
        self.assertTrue(callable(execute_append_to_doc))
        self.assertTrue(callable(execute_create_email_draft))

    def test_02_mcp_append_to_doc(self):
        from mcp_server import execute_append_to_doc
        payload = {"doc_id": "test-doc-123", "content": "Weekly Pulse Test Content"}
        status_code, data = execute_append_to_doc(payload)
        self.assertEqual(status_code, 200)
        self.assertEqual(data.get("status"), "success")
        self.assertIn("document_url", data)
        self.assertIn("bytes_appended", data)

    def test_03_mcp_create_email_draft(self):
        from mcp_server import execute_create_email_draft
        payload = {
            "to": "test@example.com",
            "subject": "Weekly Pulse Subject",
            "body": "Weekly Pulse Body"
        }
        status_code, data = execute_create_email_draft(payload)
        self.assertEqual(status_code, 200)
        self.assertEqual(data.get("status"), "success")
        self.assertIn("draft_id", data)
        self.assertEqual(data.get("recipient"), "test@example.com")

    def test_04_phase9_and_phase10_execution(self):
        # Run Phase 9
        res = subprocess.run([sys.executable, str(PROJECT_ROOT / "phase9" / "publish_to_docs.py")], cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Phase 9 failed: {res.stderr}")

        # Run Phase 10
        res = subprocess.run([sys.executable, str(PROJECT_ROOT / "phase10" / "create_email_draft.py")], cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Phase 10 failed: {res.stderr}")

    def test_05_phase11_validation_report(self):
        # Run Phase 11
        res = subprocess.run([sys.executable, str(PROJECT_ROOT / "phase11" / "validate_workflow.py")], cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Phase 11 failed: {res.stdout}\n{res.stderr}")

        report_path = PROJECT_ROOT / "phase11" / "data" / "validation" / "phase11_validation_report.json"
        self.assertTrue(report_path.exists())
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        self.assertTrue(report.get("overall_valid"))
        constraints = report.get("constraints_met", {})
        self.assertTrue(constraints.get("max_5_themes"))
        self.assertTrue(constraints.get("top_3_themes_in_report"))
        self.assertTrue(constraints.get("3_real_quotes"))
        self.assertTrue(constraints.get("3_action_ideas"))
        self.assertTrue(constraints.get("mcp_docs_integration"))
        self.assertTrue(constraints.get("mcp_gmail_integration"))
        self.assertTrue(constraints.get("privacy_protection"))

    def test_06_phase12_submission_preparation(self):
        # Run Phase 12
        res = subprocess.run([sys.executable, str(PROJECT_ROOT / "phase12" / "prepare_submission.py")], cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Phase 12 failed: {res.stderr}")

        summary_path = PROJECT_ROOT / "phase12" / "data" / "submission" / "phase12_submission_summary.json"
        self.assertTrue(summary_path.exists())
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        self.assertTrue(summary["status"]["documentation_complete"])
        self.assertTrue(summary["status"]["all_outputs_generated"])
        self.assertTrue(summary["status"]["workflow_validated"])


if __name__ == "__main__":
    unittest.main()
