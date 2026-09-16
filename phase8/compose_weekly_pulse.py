"""
Phase 8: Weekly Pulse Composition

Composes a concise weekly pulse draft from selected themes, quotes, and actions.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent.parent / "phase5"))
from groq_client import call_groq_json

PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?\d[\s-]?){10,14}\b"),
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_text(text, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def compose_markdown_from_structured(data):
    today = datetime.now().strftime("%Y-%m-%d")
    headline = data.get("headline", "Weekly Review Pulse")
    top_themes = data.get("top_themes", [])
    quotes = data.get("quotes", [])
    action_items = data.get("actions", [])

    lines = [
        f"# Weekly Review Pulse - {today}",
        "",
        f"**{headline}**",
        "",
        "## Top Themes",
    ]

    for index, theme in enumerate(top_themes, start=1):
        label = theme.get("label", "Theme")
        description = theme.get("description", "")
        lines.append(f"{index}. **{label}**")
        if description:
            lines.append(f"   {description}")

    lines.extend(["", "## Real Quotes"])
    for quote in quotes:
        lines.append(f'- "{quote}"')

    lines.extend(["", "## Action Ideas"])
    for index, action in enumerate(action_items, start=1):
        lines.append(f"{index}. {action}")

    lines.append("")
    return "\n".join(lines)


def build_fallback_structured(prioritized, actions):
    top_themes = prioritized.get("top_themes", [])[:3]
    selected_quotes = prioritized.get("selected_quotes", [])[:3]
    action_items = actions.get("actions", [])[:3]

    return {
        "headline": "Weekly review analysis highlights key user concerns and improvement opportunities",
        "top_themes": [
            {
                "label": theme.get("theme_name", "Theme"),
                "description": theme.get("summary", ""),
            }
            for theme in top_themes
        ],
        "quotes": [
            (q.get("quote", "") if isinstance(q, dict) else str(q))[:240]
            for q in selected_quotes
        ],
        "actions": [
            action.get("action", "")
            for action in action_items
        ],
    }


def validate_pulse(markdown):
    findings = {}
    for name, pattern in PII_PATTERNS.items():
        matches = pattern.findall(markdown)
        if matches:
            findings[name] = matches
    return {
        "pii_findings": findings,
        "ready_for_delivery": len(findings) == 0,
        "external_api_calls": 0,
    }


def compose_with_groq(project_root, prioritized, actions):
    system_prompt = (
        "You compose a concise stakeholder-ready weekly app review pulse. "
        "Return only valid JSON with exactly this schema: "
        '{"headline":"...","top_themes":[{"label":"...","description":"..."}],'
        '"quotes":["...","...","..."],"actions":["...","...","..."]}. '
        "The headline should be a 1-sentence summary of the overall sentiment. "
        "Top themes must have label and description. "
        "Quotes must be the exact real quotes provided. "
        "Actions must be concise 1-sentence recommendations. "
        "Do not invent quotes or include PII."
    )
    compact_themes = [
        {
            "theme_name": theme.get("theme_name"),
            "review_count": theme.get("review_count"),
            "sentiment": theme.get("sentiment"),
            "summary": theme.get("summary"),
        }
        for theme in prioritized.get("top_themes", [])[:3]
    ]
    compact_quotes = []
    for quote in prioritized.get("selected_quotes", [])[:3]:
        text = quote.get("quote", "") if isinstance(quote, dict) else str(quote)
        compact_quotes.append(text[:240])
    compact_actions = [
        action.get("action", "")
        for action in actions.get("actions", [])[:3]
    ]
    payload = {
        "top_themes": compact_themes,
        "selected_quotes": compact_quotes,
        "actions": compact_actions,
    }
    result = call_groq_json(project_root, system_prompt, payload, max_tokens=900)
    if not result["ok"]:
        return None, {
            "ok": False,
            "error": result["error"],
            "usage": {},
        }, "local_deterministic_fallback_after_groq_error"
    data = result["data"]
    return data, {
        "ok": True,
        "error": None,
        "usage": result.get("usage", {}),
    }, "groq"


def main():
    project_root = Path(__file__).resolve().parent.parent
    prioritized_path = project_root / "phase6" / "data" / "prioritized" / "prioritized_themes.json"
    actions_path = project_root / "phase7" / "data" / "actions" / "action_ideas.json"
    output_dir = project_root / "phase8" / "data" / "weekly_pulse"
    pulse_json_path = output_dir / "weekly_pulse.json"
    pulse_md_path = output_dir / "weekly_pulse.md"
    validation_path = output_dir / "weekly_pulse_validation.json"
    status_path = output_dir / "phase8_groq_status.json"

    if not prioritized_path.exists():
        raise FileNotFoundError(f"Phase 6 prioritized themes not found: {prioritized_path}")
    if not actions_path.exists():
        raise FileNotFoundError(f"Phase 7 actions not found: {actions_path}")

    prioritized = load_json(str(prioritized_path))
    actions = load_json(str(actions_path))

    structured, groq_status, source = compose_with_groq(str(project_root), prioritized, actions)
    if structured is None:
        structured = build_fallback_structured(prioritized, actions)

    markdown = compose_markdown_from_structured(structured)
    validation = validate_pulse(markdown)

    save_json(structured, str(pulse_json_path))
    save_json(validation, str(validation_path))
    save_json(groq_status, str(status_path))
    save_text(markdown, str(pulse_md_path))

    print("=" * 60)
    print("Phase 8: Weekly Pulse Composition")
    print("=" * 60)
    print(f"Source: {source}")
    print(f"External API calls: {1 if source == 'groq' else 0}")
    print(f"Ready for delivery: {validation['ready_for_delivery']}")
    print(f"Weekly pulse saved to: {pulse_md_path}")
    print(f"Weekly pulse JSON saved to: {pulse_json_path}")


if __name__ == "__main__":
    main()
