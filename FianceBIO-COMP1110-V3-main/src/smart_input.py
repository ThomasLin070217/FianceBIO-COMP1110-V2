"""
Helpers for parsing loosely structured transaction input.
"""
import re

try:
    from validator import ALLOWED_CATEGORIES
except ModuleNotFoundError:
    from src.validator import ALLOWED_CATEGORIES


CATEGORY_SYNONYMS = {
    "dining": "Dining",
    "food": "Dining",
    "meal": "Dining",
    "lunch": "Dining",
    "dinner": "Dining",
    "housing": "Housing",
    "rent": "Housing",
    "transport": "Transport",
    "mtr": "Transport",
    "bus": "Transport",
    "taxi": "Transport",
    "academic": "Academic",
    "book": "Academic",
    "tuition": "Academic",
    "social": "Social",
    "party": "Social",
    "digital": "Digital",
    "subscription": "Digital",
    "income": "Income",
    "salary": "Income",
    "other": "Other",
}


def _normalize_date(raw_text):
    # Support YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD
    match = re.search(r"\b(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})\b", raw_text)
    if not match:
        return None, raw_text

    y, m, d = match.group(1), int(match.group(2)), int(match.group(3))
    normalized = f"{y}-{m:02d}-{d:02d}"
    cleaned = raw_text.replace(match.group(0), " ")
    return normalized, cleaned


def _extract_amount(raw_text):
    match = re.search(r"(?:hkd|\$)?\s*(\d+(?:\.\d+)?)", raw_text, flags=re.IGNORECASE)
    if not match:
        return None, raw_text
    amount = match.group(1)
    cleaned = raw_text.replace(match.group(0), " ")
    return amount, cleaned


def _extract_category(raw_text):
    lowered = raw_text.lower()
    for key, normalized in CATEGORY_SYNONYMS.items():
        if re.search(rf"\b{re.escape(key)}\b", lowered):
            cleaned = re.sub(rf"\b{re.escape(key)}\b", " ", raw_text, flags=re.IGNORECASE)
            return normalized, cleaned

    for category in ALLOWED_CATEGORIES:
        if re.search(rf"\b{re.escape(category)}\b", lowered):
            cleaned = re.sub(rf"\b{re.escape(category)}\b", " ", raw_text, flags=re.IGNORECASE)
            return category, cleaned

    return None, raw_text


def parse_unstructured_transaction(raw_text):
    """
    Parse text like:
    "2026/04/21 spent $65.5 on food CYM roast goose rice"
    Returns a dict with date/amount/category/description when possible.
    """
    if not raw_text or not raw_text.strip():
        return None

    date, remaining = _normalize_date(raw_text)
    amount, remaining = _extract_amount(remaining)
    category, remaining = _extract_category(remaining)

    description = re.sub(r"\s+", " ", remaining).strip(" ,.-")
    if not description:
        description = "Quick entry"

    return {
        "date": date,
        "amount": amount,
        "category": category,
        "description": description,
    }
