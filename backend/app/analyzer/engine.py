import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Set


@lru_cache(maxsize=1)
def load_rules() -> Dict:
    config_path = Path(__file__).resolve().parent.parent / "config" / "rules.json"
    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_any(text: str, terms: List[str]) -> List[str]:
    matches = []
    for term in terms:
        if term in text:
            matches.append(term)
    return matches


def _extract_keywords(message: str, rules: Dict) -> List[str]:
    extraction_rules = rules["keyword_extraction"]
    min_len = extraction_rules["min_word_length"]
    max_keywords = extraction_rules["max_keywords"]
    stopwords: Set[str] = set(extraction_rules["stopwords"])

    words = re.findall(r"[a-zA-Z0-9']+", message.lower())
    filtered = [
        word
        for word in words
        if len(word) >= min_len and word not in stopwords and not word.isdigit()
    ]

    frequencies: Dict[str, int] = {}
    for word in filtered:
        frequencies[word] = frequencies.get(word, 0) + 1

    ranked = sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))
    return [word for word, _ in ranked[:max_keywords]]


def analyze_ticket(message: str) -> Dict:
    rules = load_rules()
    normalized = _normalize(message)
    signals: List[str] = []

    category_scores = {category: 0 for category in rules["categories"].keys()}
    matched_category_terms: Dict[str, List[str]] = {k: [] for k in category_scores.keys()}

    for category, terms in rules["categories"].items():
        matches = _contains_any(normalized, terms)
        category_scores[category] += len(matches)
        matched_category_terms[category].extend(matches)

    best_category = "Other"
    best_score = 0
    for category, score in category_scores.items():
        if score > best_score:
            best_category = category
            best_score = score

    urgency_matches = _contains_any(normalized, rules["urgency_terms"])
    urgency = "High" if urgency_matches else "Normal"
    if urgency_matches:
        signals.extend([f"urgency:{term}" for term in urgency_matches])

    priority = "P3"
    severity_rules = rules["severity_terms"]
    for level in ["P0", "P1", "P2", "P3"]:
        if _contains_any(normalized, severity_rules[level]):
            priority = level
            signals.append(f"severity:{level}")
            break

    if priority == "P3":
        if urgency == "High" and best_category in {"Technical", "Account"}:
            priority = "P1"
        elif urgency == "High":
            priority = "P2"
        elif best_category in {"Billing", "Technical", "Account"}:
            priority = "P2"

    # Custom rule: always treat security incidents as critical technical issues.
    custom_rule = rules["custom_rules"]["security_override"]
    security_matches = _contains_any(normalized, custom_rule["keywords"])
    if security_matches:
        best_category = custom_rule["set_category"]
        priority = custom_rule["set_priority"]
        signals.append("custom:security_override")

    if best_category != "Other" and matched_category_terms.get(best_category):
        signals.extend([f"category:{term}" for term in matched_category_terms[best_category]])

    match_count = best_score + len(urgency_matches) + len(security_matches)
    confidence = min(0.99, round(0.35 + (match_count * 0.12), 2))
    if best_category == "Other" and not urgency_matches and not security_matches:
        confidence = 0.4

    keywords = _extract_keywords(message, rules)

    return {
        "category": best_category,
        "priority": priority,
        "urgency": urgency,
        "confidence": confidence,
        "signals": sorted(set(signals)),
        "keywords": keywords,
    }
