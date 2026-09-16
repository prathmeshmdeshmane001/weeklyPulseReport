"""
Phase 6: Theme Prioritization and Evidence Selection

Ranks Phase 5 themes locally and selects top themes plus real privacy-safe quotes.
"""

import json
import os
from pathlib import Path


TOP_THEME_LIMIT = 3
QUOTE_LIMIT = 3


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def negative_share(theme):
    breakdown = theme.get("rating_breakdown", {})
    total = sum(breakdown.values()) or 1
    return breakdown.get("negative", 0) / total


def theme_priority_score(theme):
    review_count = theme.get("review_count", 0)
    return review_count + int(negative_share(theme) * 100)


def normalize_quote(quote):
    if isinstance(quote, str):
        return {"quote": quote, "rating_label": "unknown", "rating": 0}
    if isinstance(quote, dict):
        return {
            "quote": quote.get("quote", ""),
            "rating_label": quote.get("rating_label", "unknown"),
            "rating": quote.get("rating", 0),
            "review_id": quote.get("review_id"),
            "platform": quote.get("platform"),
        }
    return {"quote": str(quote), "rating_label": "unknown", "rating": 0}


def select_best_quote(theme):
    raw_quotes = theme.get("sample_quotes", []) or []
    quotes = [normalize_quote(q) for q in raw_quotes if q]
    if not quotes:
        return None
    sorted_quotes = sorted(
        quotes,
        key=lambda q: (
            q.get("rating_label") == "negative",
            len(q.get("quote", "").split()),
            q.get("rating", 0),
        ),
        reverse=True,
    )
    selected = dict(sorted_quotes[0])
    selected["theme_name"] = theme.get("theme_name")
    return selected


def prioritize(theme_analysis):
    themes = theme_analysis.get("themes", [])
    ranked = sorted(themes, key=theme_priority_score, reverse=True)
    top_themes = ranked[:TOP_THEME_LIMIT]

    selected_quotes = []
    for theme in top_themes:
        quote = select_best_quote(theme)
        if quote:
            selected_quotes.append(quote)
        if len(selected_quotes) >= QUOTE_LIMIT:
            break

    return {
        "source": "local_deterministic_ranking",
        "groq_calls_used": 0,
        "selection_rules": {
            "top_theme_limit": TOP_THEME_LIMIT,
            "quote_limit": QUOTE_LIMIT,
            "priority_score": "review_count plus negative sentiment share",
            "quote_rule": "real privacy-safe quote from Phase 5 sample evidence",
        },
        "top_themes": top_themes,
        "selected_quotes": selected_quotes,
    }


def main():
    project_root = Path(__file__).resolve().parent.parent
    input_path = project_root / "phase5" / "data" / "themes" / "theme_analysis.json"
    output_dir = project_root / "phase6" / "data" / "prioritized"
    output_path = output_dir / "prioritized_themes.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Phase 5 theme analysis not found: {input_path}")

    theme_analysis = load_json(str(input_path))
    result = prioritize(theme_analysis)
    save_json(result, str(output_path))

    print("=" * 60)
    print("Phase 6: Theme Prioritization and Evidence Selection")
    print("=" * 60)
    print(f"Top themes selected: {len(result['top_themes'])}")
    print(f"Quotes selected: {len(result['selected_quotes'])}")
    for theme in result["top_themes"]:
        print(f"  - {theme['theme_name']}: {theme['review_count']} reviews")
    print(f"\nPrioritized output saved to: {output_path}")


if __name__ == "__main__":
    main()
