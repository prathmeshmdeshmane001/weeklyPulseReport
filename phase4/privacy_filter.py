"""
Phase 4: Privacy Protection and Safety Review

Masks personally identifiable information from normalized reviews before AI analysis.
"""

import json
import os
import re
import sys
from copy import deepcopy
from pathlib import Path


PII_PATTERNS = [
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[EMAIL]"),
    ("phone", re.compile(r"(?<!\d)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}(?!\d)"), "[PHONE]"),
    ("username", re.compile(r"(?<!\w)@[A-Za-z0-9_]{3,30}\b"), "[USERNAME]"),
    ("ip_address", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[IP_ADDRESS]"),
    ("account_id", re.compile(r"\b(?:account|acct|customer|user|client)[\s_-]*(?:id|number|no)?[:#\s-]*[A-Za-z0-9-]{5,}\b", re.IGNORECASE), "[ACCOUNT_ID]"),
    ("order_id", re.compile(r"\b(?:order|ticket|case|reference|ref)[\s_-]*(?:id|number|no)?[:#\s-]*[A-Za-z0-9-]{5,}\b", re.IGNORECASE), "[REFERENCE_ID]"),
    ("device_id", re.compile(r"\b(?:imei|serial|device)[\s_-]*(?:id|number|no)?[:#\s-]*[A-Za-z0-9-]{6,}\b", re.IGNORECASE), "[DEVICE_ID]"),
    ("long_numeric_id", re.compile(r"\b\d{8,}\b"), "[NUMERIC_ID]"),
    ("address", re.compile(r"\b\d{1,5}\s+[A-Za-z0-9 .'-]+\s+(?:street|st|road|rd|avenue|ave|lane|ln|drive|dr|block|sector)\b", re.IGNORECASE), "[ADDRESS]"),
    ("full_name_phrase", re.compile(r"\b(?:my name is|this is|i am|i'm)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b"), "[NAME]"),
]

TEXT_FIELDS_TO_SCAN = ["review_text", "review_title"]


def mask_pii_in_text(text):
    """Mask known PII patterns in a text string and return masked text plus counts."""
    if text is None:
        return "", {}

    masked_text = str(text)
    detection_counts = {}

    for pii_type, pattern, replacement in PII_PATTERNS:
        masked_text, count = pattern.subn(replacement, masked_text)
        if count:
            detection_counts[pii_type] = detection_counts.get(pii_type, 0) + count

    masked_text = " ".join(masked_text.split())
    return masked_text, detection_counts


def merge_counts(target, source):
    """Merge PII detection counts."""
    for key, value in source.items():
        target[key] = target.get(key, 0) + value


def privacy_filter_review(review):
    """Return a privacy-safe review and per-review PII findings."""
    safe_review = deepcopy(review)
    review_findings = {}

    for field in TEXT_FIELDS_TO_SCAN:
        masked_value, counts = mask_pii_in_text(safe_review.get(field, ""))
        safe_review[field] = masked_value
        merge_counts(review_findings, counts)

    safe_review["privacy_checked"] = True
    safe_review["pii_detected"] = bool(review_findings)
    safe_review["pii_types_detected"] = sorted(review_findings.keys())

    return safe_review, review_findings


def privacy_filter_reviews(reviews):
    """Apply privacy filtering to all reviews and return safe output plus report."""
    safe_reviews = []
    total_counts = {}
    affected_reviews = []

    for index, review in enumerate(reviews, start=1):
        safe_review, findings = privacy_filter_review(review)
        safe_reviews.append(safe_review)
        if findings:
            affected_reviews.append({
                "index": index,
                "review_id": review.get("review_id", "unknown"),
                "pii_types": sorted(findings.keys()),
            })
            merge_counts(total_counts, findings)

    report = {
        "input_count": len(reviews),
        "privacy_safe_count": len(safe_reviews),
        "reviews_with_pii": len(affected_reviews),
        "pii_detection_counts": total_counts,
        "affected_reviews": affected_reviews,
        "fields_scanned": TEXT_FIELDS_TO_SCAN,
        "ready_for_ai_analysis": True,
    }

    return safe_reviews, report


def validate_no_pii_remaining(reviews):
    """Scan privacy-safe reviews again and report if any PII remains."""
    remaining = []
    for index, review in enumerate(reviews, start=1):
        combined_counts = {}
        for field in TEXT_FIELDS_TO_SCAN:
            _, counts = mask_pii_in_text(review.get(field, ""))
            merge_counts(combined_counts, counts)
        if combined_counts:
            remaining.append({
                "index": index,
                "review_id": review.get("review_id", "unknown"),
                "remaining_pii_types": sorted(combined_counts.keys()),
            })
    return remaining


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    project_root = Path(__file__).resolve().parent.parent
    input_path = project_root / "phase3" / "data" / "normalized" / "normalized_reviews.json"
    output_dir = project_root / "phase4" / "data" / "privacy_safe"
    output_path = output_dir / "privacy_safe_reviews.json"
    report_path = output_dir / "privacy_report.json"

    if not input_path.exists():
        print(f"Phase 3 normalized data not found: {input_path}")
        print("Run: python phase3/normalize_reviews.py")
        sys.exit(1)

    print("=" * 60)
    print("Phase 4: Privacy Protection and Safety Review")
    print("=" * 60)
    print(f"\nLoading normalized reviews from: {input_path}")

    reviews = load_json(str(input_path))
    safe_reviews, report = privacy_filter_reviews(reviews)
    remaining_pii = validate_no_pii_remaining(safe_reviews)
    report["remaining_pii_after_filter"] = remaining_pii
    report["ready_for_ai_analysis"] = len(remaining_pii) == 0

    save_json(safe_reviews, str(output_path))
    save_json(report, str(report_path))

    print(f"\nInput reviews: {report['input_count']}")
    print(f"Privacy-safe reviews: {report['privacy_safe_count']}")
    print(f"Reviews with PII detected: {report['reviews_with_pii']}")
    print(f"PII detection counts: {report['pii_detection_counts']}")
    print(f"Remaining PII after filter: {len(remaining_pii)}")
    print(f"Ready for AI analysis: {report['ready_for_ai_analysis']}")
    print(f"\nPrivacy-safe reviews saved to: {output_path}")
    print(f"Privacy report saved to: {report_path}")
    print("\n" + "=" * 60)
    print("Privacy filtering complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
