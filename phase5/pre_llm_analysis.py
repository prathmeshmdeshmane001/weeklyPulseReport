"""
Phase 5: API-Free Theme Analysis

Creates a capped 500-review working set, local candidate themes, and a
deterministic theme analysis output without external API calls.
"""

import json
import os
from collections import Counter, defaultdict
from pathlib import Path

from groq_client import call_groq_json


WORKING_SET_LIMIT = 500
MAX_FINAL_THEMES = 5
MAX_SNIPPETS_PER_THEME = 8

THEME_KEYWORDS = {
    "App Stability and Crashes": ["crash", "crashes", "crashed", "freeze", "freezes", "hang", "hangs", "lag", "slow", "splash"],
    "Payments and Transfers": ["payment", "payments", "pay", "upi", "merchant", "checkout", "pos", "qr", "transfer", "transfers"],
    "KYC and Onboarding": ["kyc", "onboarding", "verification", "verify", "otp", "selfie", "document", "aadhaar", "pan", "address"],
    "Withdrawals": ["withdrawal", "withdraw", "bank", "credit", "limit", "fee", "wallet"],
    "Customer Support": ["support", "customer", "ticket", "chat", "call", "respond", "response", "resolved", "agent"],
    "Product Experience and Features": ["ui", "interface", "design", "feature", "dark", "mode", "analytics", "budget", "rewards", "cashback", "notifications"],
}

STOPWORDS = {
    "the", "and", "for", "this", "that", "with", "app", "my", "has", "have", "had", "was", "were", "are", "but",
    "not", "all", "very", "from", "when", "every", "time", "after", "before", "into", "than", "too", "now",
    "use", "using", "used", "try", "tried", "get", "got", "can", "cannot", "could", "would", "should", "really",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def tokenize(text):
    token = ""
    tokens = []
    for char in text.lower():
        if char.isalnum():
            token += char
        else:
            if token:
                tokens.append(token)
                token = ""
    if token:
        tokens.append(token)
    return [t for t in tokens if len(t) > 2 and t not in STOPWORDS]


def detect_themes_for_review(review_text):
    text = review_text.lower()
    matched = []
    for theme, keywords in THEME_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            matched.append(theme)
    return matched or ["Other"]


def quote_quality_score(review):
    text = review.get("review_text", "")
    word_count = len(text.split())
    rating_label = review.get("rating_label", "neutral")
    sentiment_bonus = 5 if rating_label == "negative" else 2 if rating_label == "neutral" else 1
    return min(word_count, 40) + sentiment_bonus + int(review.get("thumbs_up_count", 0) or 0)


def enrich_reviews(reviews):
    enriched = []
    for review in reviews:
        item = dict(review)
        item["detected_themes"] = detect_themes_for_review(item.get("review_text", ""))
        item["quote_quality_score"] = quote_quality_score(item)
        enriched.append(item)
    return enriched


def select_representative_working_set(reviews, limit=WORKING_SET_LIMIT):
    enriched = enrich_reviews(reviews)
    buckets = defaultdict(list)
    for review in enriched:
        primary_theme = review["detected_themes"][0]
        buckets[(primary_theme, review.get("rating_label", "neutral"))].append(review)

    for bucket_reviews in buckets.values():
        bucket_reviews.sort(key=lambda r: (r.get("date", ""), r["quote_quality_score"]), reverse=True)

    selected = []
    seen = set()
    keys = sorted(buckets, key=lambda key: len(buckets[key]), reverse=True)
    while len(selected) < min(limit, len(enriched)):
        added = False
        for key in keys:
            while buckets[key] and buckets[key][0]["review_id"] in seen:
                buckets[key].pop(0)
            if buckets[key] and len(selected) < limit:
                review = buckets[key].pop(0)
                selected.append(review)
                seen.add(review["review_id"])
                added = True
        if not added:
            break
    return selected


def summarize_theme(theme, rating_breakdown):
    negative = rating_breakdown.get("negative", 0)
    positive = rating_breakdown.get("positive", 0)
    if negative > positive:
        sentiment = "mostly_negative"
    elif positive > negative:
        sentiment = "mostly_positive"
    else:
        sentiment = "mixed"
    return {
        "theme_name": theme,
        "summary": f"Users repeatedly mention {theme.lower()} in recent reviews.",
        "sentiment": sentiment,
    }


def analyze_reviews(reviews, source_review_count):
    rating_counts = Counter(review["rating_label"] for review in reviews)
    platform_counts = Counter(review["platform"] for review in reviews)
    theme_counts = Counter()
    theme_rating_counts = defaultdict(Counter)
    theme_examples = defaultdict(list)
    theme_review_ids = defaultdict(list)
    word_counts = Counter()

    for review in reviews:
        text = review.get("review_text", "")
        themes = review.get("detected_themes") or detect_themes_for_review(text)
        for theme in themes:
            theme_counts[theme] += 1
            theme_rating_counts[theme][review["rating_label"]] += 1
            theme_review_ids[theme].append(review["review_id"])
            if len(theme_examples[theme]) < MAX_SNIPPETS_PER_THEME:
                theme_examples[theme].append({
                    "review_id": review["review_id"],
                    "rating": review["rating"],
                    "rating_label": review["rating_label"],
                    "platform": review["platform"],
                    "quote": text[:280],
                })
        word_counts.update(tokenize(text))

    candidate_themes = []
    final_themes = []
    for theme, count in theme_counts.most_common():
        rating_breakdown = dict(theme_rating_counts[theme])
        candidate_themes.append({
            "theme": theme,
            "review_count": count,
            "rating_breakdown": rating_breakdown,
            "sample_quotes": theme_examples[theme],
        })
        if theme != "Other" and len(final_themes) < MAX_FINAL_THEMES:
            theme_summary = summarize_theme(theme, rating_breakdown)
            final_themes.append({
                **theme_summary,
                "review_count": count,
                "rating_breakdown": rating_breakdown,
                "supporting_review_ids": theme_review_ids[theme][:50],
                "sample_quotes": theme_examples[theme][:5],
                "source": "local_deterministic_fallback",
            })

    report = {
        "source_review_count": source_review_count,
        "working_set_limit": WORKING_SET_LIMIT,
        "review_count": len(reviews),
        "rating_label_counts": dict(rating_counts),
        "platform_counts": dict(platform_counts),
        "candidate_themes": candidate_themes,
        "top_keywords": word_counts.most_common(30),
        "api_free_strategy": {
            "external_api_calls": 0,
            "working_set_limit": WORKING_SET_LIMIT,
            "method": "Deterministic keyword grouping, sentiment counts, representative evidence, and local theme summaries.",
            "expected_output": "Up to 5 themes with name, summary, review_count, sentiment, and supporting review_ids.",
        },
    }
    theme_analysis = {
        "provider": "local_deterministic",
        "external_api_calls": 0,
        "source_review_count": source_review_count,
        "working_set_review_count": len(reviews),
        "max_themes": MAX_FINAL_THEMES,
        "themes": final_themes,
    }
    return report, theme_analysis


def compact_theme_payload(report):
    candidate_themes = []
    for theme in report["candidate_themes"]:
        candidate_themes.append({
            "theme": theme["theme"],
            "review_count": theme["review_count"],
            "rating_breakdown": theme["rating_breakdown"],
            "sample_quotes": theme["sample_quotes"][:3],
        })
    return {
        "source_review_count": report["source_review_count"],
        "working_set_review_count": report["review_count"],
        "max_themes": MAX_FINAL_THEMES,
        "candidate_themes": candidate_themes,
        "top_keywords": report["top_keywords"][:20],
    }


def refine_themes_with_groq(project_root, report, fallback_theme_analysis):
    system_prompt = (
        "You refine app review theme analysis. Return only valid JSON. "
        "Use only the provided candidate themes, review counts, source review IDs, and real quotes. "
        "Do not invent quotes or evidence. Return up to 5 themes in this schema: "
        "{\"provider\":\"groq\",\"external_api_calls\":1,\"source_review_count\":number,"
        "\"working_set_review_count\":number,\"max_themes\":number,\"themes\":[{\"theme_name\":\"\","
        "\"summary\":\"\",\"sentiment\":\"mostly_negative|mostly_positive|mixed\",\"review_count\":number,"
        "\"rating_breakdown\":{},\"supporting_review_ids\":[],\"sample_quotes\":[]}]}"
    )
    result = call_groq_json(project_root, system_prompt, compact_theme_payload(report), max_tokens=2200)
    if not result["ok"]:
        fallback_theme_analysis["provider"] = "local_deterministic_fallback_after_groq_error"
        fallback_theme_analysis["groq_error"] = result["error"]
        return fallback_theme_analysis, {
            "ok": False,
            "error": result["error"],
            "usage": {},
        }
    data = result["data"]
    data["provider"] = "groq"
    data["external_api_calls"] = 1
    return data, {
        "ok": True,
        "error": None,
        "usage": result.get("usage", {}),
    }


def main():
    project_root = Path(__file__).resolve().parent.parent
    input_path = project_root / "phase4" / "data" / "privacy_safe" / "privacy_safe_reviews.json"
    pre_llm_dir = project_root / "phase5" / "data" / "pre_llm"
    themes_dir = project_root / "phase5" / "data" / "themes"

    reviews = load_json(str(input_path))
    working_set = select_representative_working_set(reviews)
    report, theme_analysis = analyze_reviews(working_set, len(reviews))
    theme_analysis, groq_status = refine_themes_with_groq(str(project_root), report, theme_analysis)

    save_json(working_set, str(pre_llm_dir / "phase5_working_set_reviews.json"))
    save_json(report, str(pre_llm_dir / "pre_llm_analysis_report.json"))
    save_json(groq_status, str(pre_llm_dir / "phase5_groq_status.json"))
    save_json(theme_analysis, str(themes_dir / "theme_analysis.json"))

    print("=" * 60)
    print("Phase 5: API-Free Theme Analysis")
    print("=" * 60)
    print(f"Source privacy-safe reviews: {len(reviews)}")
    print(f"Working set reviews: {report['review_count']}")
    print(f"Provider: {theme_analysis['provider']}")
    print(f"External API calls: {theme_analysis.get('external_api_calls', 0)}")
    print(f"Rating distribution: {report['rating_label_counts']}")
    print("\nCandidate themes:")
    for theme in report["candidate_themes"]:
        print(f"  - {theme['theme']}: {theme['review_count']} reviews | {theme['rating_breakdown']}")
    print(f"\nTheme analysis saved to: {themes_dir / 'theme_analysis.json'}")


if __name__ == "__main__":
    main()
