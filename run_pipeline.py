"""
Weekly Review Pulse - End-to-End Pipeline Orchestrator

Executes all pipeline phases in order, handles environment configuration,
ensures MCP server connectivity, syncs artifacts to frontend, and validates results.

Usage:
    python run_pipeline.py               # Run all phases 2-12
    python run_pipeline.py --phases 2-8  # Run specific phases
    python run_pipeline.py --start-mcp   # Start MCP server and run pipeline
    python run_pipeline.py --status      # Check current pipeline status
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def load_env():
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        example = PROJECT_ROOT / ".env.example"
        if example.exists():
            shutil.copy(example, env_file)
            print("Notice: Initialized .env from .env.example")
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")


def is_mcp_server_running(url):
    try:
        req = urllib.request.Request(f"{url.rstrip('/')}/health", headers={"User-Agent": "PipelineRunner"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def start_local_mcp_server():
    server_script = PROJECT_ROOT / "mcp_server.py"
    if not server_script.exists():
        return None
    proc = subprocess.Popen(
        [sys.executable, str(server_script)],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    # Give server a moment to bind
    for _ in range(10):
        time.sleep(0.3)
        if is_mcp_server_running(os.environ.get("MCP_SERVER_URL", "http://localhost:8000")):
            return proc
    return proc


def run_phase_script(script_path, description):
    print(f"\n▶ Running {description} ({script_path.name})...")
    start_time = time.time()
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True
    )
    elapsed = time.time() - start_time
    if result.returncode == 0:
        print(f"  ✔ {description} completed in {elapsed:.2f}s")
        if result.stdout:
            # Print brief summary from stdout
            lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
            for line in lines[-4:]:
                print(f"    {line}")
        return True, result.stdout
    else:
        print(f"  ✖ {description} FAILED (exit {result.returncode}) in {elapsed:.2f}s")
        if result.stderr:
            print("  Error output:")
            for line in result.stderr.strip().splitlines():
                print(f"    {line}")
        elif result.stdout:
            print("  Stdout:")
            for line in result.stdout.strip().splitlines()[-6:]:
                print(f"    {line}")
        return False, result.stderr or result.stdout


def sync_frontend_data():
    """Copy latest pipeline outputs to frontend/public/data so dashboard is instantly live."""
    public_data_dir = PROJECT_ROOT / "frontend" / "public" / "data"
    public_data_dir.mkdir(parents=True, exist_ok=True)

    sources = [
        ("phase4/data/privacy_safe/privacy_safe_reviews.json", "privacy_safe_reviews.json"),
        ("phase8/data/weekly_pulse/weekly_pulse.json", "weekly_pulse.json"),
        ("phase8/data/weekly_pulse/weekly_pulse.md", "weekly_pulse.md"),
        ("phase9/data/docs_delivery/phase9_delivery_status.json", "phase9_delivery_status.json"),
        ("phase10/data/gmail_delivery/phase10_gmail_status.json", "phase10_gmail_status.json"),
        ("phase11/data/validation/phase11_validation_report.json", "phase11_validation_report.json"),
    ]

    copied = 0
    for src_rel, dst_name in sources:
        src = PROJECT_ROOT / src_rel
        if src.exists():
            shutil.copy2(src, public_data_dir / dst_name)
            copied += 1
    print(f"\n✔ Synced {copied} data artifacts to frontend/public/data/")


def main():
    parser = argparse.ArgumentParser(description="Run the Weekly Review Pulse Pipeline.")
    parser.add_argument("--phases", default="all", help="Phases to run (e.g., 'all', '2-8', '2,3,4')")
    parser.add_argument("--start-mcp", action="store_true", help="Start local MCP server before running")
    parser.add_argument("--status", action="store_true", help="Check pipeline status and exit")
    args = parser.parse_args()

    load_env()

    if args.status:
        val_report = PROJECT_ROOT / "phase11" / "data" / "validation" / "phase11_validation_report.json"
        if val_report.exists():
            with open(val_report, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(json.dumps(data, indent=2))
        else:
            print("No validation report found. Run `python run_pipeline.py` first.")
        return

    mcp_url = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")
    mcp_proc = None

    if "localhost" in mcp_url or "127.0.0.1" in mcp_url:
        if not is_mcp_server_running(mcp_url):
            print(f"MCP server not responding at {mcp_url}. Starting local MCP server...")
            mcp_proc = start_local_mcp_server()
            if is_mcp_server_running(mcp_url):
                print(f"✔ Local MCP server started successfully at {mcp_url}")
            else:
                print(f"⚠ Warning: Could not start local MCP server at {mcp_url}. Delivery phases may fail.")
        else:
            print(f"✔ MCP server active at {mcp_url}")

    phases_map = {
        2: (PROJECT_ROOT / "phase2" / "ingest_reviews.py", "Phase 2: Review Ingestion"),
        3: (PROJECT_ROOT / "phase3" / "normalize_reviews.py", "Phase 3: Data Normalization"),
        4: (PROJECT_ROOT / "phase4" / "privacy_filter.py", "Phase 4: Privacy Protection"),
        5: (PROJECT_ROOT / "phase5" / "pre_llm_analysis.py", "Phase 5: Theme Analysis"),
        6: (PROJECT_ROOT / "phase6" / "prioritize_themes.py", "Phase 6: Theme Prioritization"),
        7: (PROJECT_ROOT / "phase7" / "generate_actions.py", "Phase 7: Action Generation"),
        8: (PROJECT_ROOT / "phase8" / "compose_weekly_pulse.py", "Phase 8: Pulse Composition"),
        9: (PROJECT_ROOT / "phase9" / "publish_to_docs.py", "Phase 9: Google Docs Delivery"),
        10: (PROJECT_ROOT / "phase10" / "create_email_draft.py", "Phase 10: Gmail MCP Draft"),
        11: (PROJECT_ROOT / "phase11" / "validate_workflow.py", "Phase 11: End-to-End Validation"),
        12: (PROJECT_ROOT / "phase12" / "prepare_submission.py", "Phase 12: Submission Preparation"),
    }

    if args.phases == "all":
        selected_phases = list(phases_map.keys())
    elif "-" in args.phases:
        start_p, end_p = map(int, args.phases.split("-"))
        selected_phases = [p for p in phases_map if start_p <= p <= end_p]
    else:
        selected_phases = [int(p.strip()) for p in args.phases.split(",") if p.strip().isdigit()]

    print("=" * 65)
    print("WEEKLY REVIEW PULSE - COMPLETE PIPELINE EXECUTION")
    print(f"Phases to execute: {selected_phases}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    failed = []
    for phase_num in selected_phases:
        if phase_num not in phases_map:
            continue
        script_path, description = phases_map[phase_num]
        if not script_path.exists():
            print(f"  ✖ Script missing: {script_path}")
            failed.append(phase_num)
            break
        success, _ = run_phase_script(script_path, description)
        if not success:
            failed.append(phase_num)
            # Allow continuing or stopping? For critical phases (2-8, 11), stop
            if phase_num in (2, 3, 4, 5, 6, 7, 8):
                print(f"\nPipeline halted due to failure in {description}")
                break

    sync_frontend_data()

    print("\n" + "=" * 65)
    if not failed:
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY! All phases passed.")
    else:
        print(f"⚠ Pipeline completed with issues in phases: {failed}")
    print("=" * 65)

    if mcp_proc:
        try:
            mcp_proc.terminate()
        except Exception:
            pass

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
