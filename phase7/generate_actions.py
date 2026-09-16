"""
Phase 7: Action Idea Generation

Creates grounded action ideas from top themes without external API calls.
"""

import json
import os
import sys
from pathlib import Path


ACTION_LIMIT = 3
sys.path.append(str(Path(__file__).resolve().parent.parent / "phase5"))
from groq_client import call_groq_json


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def action_for_theme(theme):
    name = theme.get("theme_name", "Review Theme")
    sentiment = theme.get("sentiment", "mixed")
    if "Support" in name:
        action = "Audit unresolved support journeys and create a weekly queue for high-frequency review complaints."
    elif "Crash" in name or "Stability" in name:
        action = "Prioritize crash and latency diagnostics for the most recent app versions mentioned in reviews."
    elif "Payment" in name or "Transfer" in name:
        action = "Review failed payment and transfer flows, then publish clearer failure-state guidance in the app."
    elif "Withdrawal" in name:
        action = "Investigate withdrawal delay patterns and improve status messaging for pending withdrawals."
    elif "KYC" in name or "Onboarding" in name:
        action = "Simplify KYC failure recovery and add clearer next-step instructions for blocked onboarding users."
    else:
        action = "Review the most common feedback examples and convert recurring friction into a product improvement backlog item."
    return {
        "theme_name": name,
        "action": action,
        "rationale": f"This action is grounded in a {sentiment} theme supported by {theme.get('review_count', 0)} reviews.",
    }


def generate_actions(prioritized):
    top_themes = prioritized.get("top_themes", [])[:ACTION_LIMIT]
    actions = [action_for_theme(theme) for theme in top_themes]
    return {
        "source": "local_deterministic",
        "external_api_calls": 0,
        "actions": actions,
    }


def generate_actions_with_groq(project_root, prioritized, fallback_actions):
    system_prompt = (
        "You generate practical product/support action ideas from app review themes. "
        "Return only valid JSON. Use only provided themes and quotes. "
        "Return schema: {\"source\":\"groq\",\"external_api_calls\":1,\"actions\":["
        "{\"theme_name\":\"\",\"action\":\"\",\"rationale\":\"\"}]}. "
        "Generate exactly 3 concrete, non-vague actions."
    )
    payload = {
        "top_themes": prioritized.get("top_themes", [])[:ACTION_LIMIT],
        "selected_quotes": prioritized.get("selected_quotes", []),
    }
    result = call_groq_json(project_root, system_prompt, payload, max_tokens=1200)
    if not result["ok"]:
        fallback_actions["source"] = "local_deterministic_fallback_after_groq_error"
        fallback_actions["groq_error"] = result["error"]
        return fallback_actions, {
            "ok": False,
            "error": result["error"],
            "usage": {},
        }
    data = result["data"]
    data["source"] = "groq"
    data["external_api_calls"] = 1
    return data, {
        "ok": True,
        "error": None,
        "usage": result.get("usage", {}),
    }


def main():
    project_root = Path(__file__).resolve().parent.parent
    input_path = project_root / "phase6" / "data" / "prioritized" / "prioritized_themes.json"
    output_dir = project_root / "phase7" / "data" / "actions"
    actions_path = output_dir / "action_ideas.json"
    status_path = output_dir / "phase7_groq_status.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Phase 6 prioritized themes not found: {input_path}")

    prioritized = load_json(str(input_path))
    actions = generate_actions(prioritized)
    actions, groq_status = generate_actions_with_groq(str(project_root), prioritized, actions)
    save_json(actions, str(actions_path))
    save_json(groq_status, str(status_path))

    print("=" * 60)
    print("Phase 7: Action Idea Generation")
    print("=" * 60)
    print(f"Actions generated: {len(actions['actions'])}")
    print(f"Source: {actions['source']}")
    print(f"External API calls: {actions.get('external_api_calls', 0)}")
    for action in actions["actions"]:
        print(f"  - {action['theme_name']}: {action['action']}")
    print(f"\nAction ideas saved to: {actions_path}")


if __name__ == "__main__":
    main()
