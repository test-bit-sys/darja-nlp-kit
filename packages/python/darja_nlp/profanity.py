"""Algerian Darja profanity, vulgarity, and toxic language detection and censorship."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

_DATA_DIR = Path(__file__).resolve().parent / "data"

SeverityType = Literal["none", "low", "medium", "high"]

@dataclass
class ProfanityMatch:
    term: str
    category: str
    severity: SeverityType
    matched_text: str
    start: int
    end: int

@dataclass
class ProfanityResult:
    is_profane: bool
    severity: SeverityType
    matches: List[ProfanityMatch] = field(default_factory=list)
    censored_text: str = ""

_profanity_data: Optional[Dict[str, Any]] = None

def load_profanity_data() -> Dict[str, Any]:
    global _profanity_data
    if _profanity_data is not None:
        return _profanity_data

    path = _DATA_DIR / "profanity.json"
    with open(path, "r", encoding="utf-8") as f:
        _profanity_data = json.load(f)
    return _profanity_data

def _normalize_for_matching(text: str) -> str:
    """Normalize repeated letters and spaces for robust insult detection."""
    t = text.lower()
    # Normalize tashkeel and elongation (tatweel)
    t = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', t)
    # Collapse repetitive chars (e.g. zzzzzebbbbb -> zeb)
    t = re.sub(r'(.)\1{2,}', r'\1\1', t)
    return t

def detect_profanity(text: str) -> ProfanityResult:
    """Detect Algerian profanities, slurs, and toxic terms in Arabic script or Arabizi."""
    if not text or not text.strip():
        return ProfanityResult(is_profane=False, severity="none", matches=[], censored_text=text)

    data = load_profanity_data()
    terms_list = data.get("terms", [])
    
    matches: List[ProfanityMatch] = []
    norm_text = _normalize_for_matching(text)
    censored = list(text)

    highest_severity: SeverityType = "none"
    severity_order = {"none": 0, "low": 1, "medium": 2, "high": 3}

    for item in terms_list:
        term_ar = item.get("ar", "")
        arabizi_variants = item.get("arabizi", [])
        category = item.get("category", "insult_street")
        severity = item.get("severity", "medium")

        variants = []
        if term_ar:
            variants.append(term_ar)
        variants.extend(arabizi_variants)

        for var in variants:
            if not var:
                continue
            # Regex word boundary pattern matching both Latin & Arabic
            # In Arabic / Darja, regex boundaries with \b can behave differently with arabic chars,
            # so we use lookbehind/lookahead or boundary check
            escaped = re.escape(var)
            pattern = re.compile(rf'(?<!\w){escaped}(?!\w)', re.IGNORECASE)
            
            for m in pattern.finditer(norm_text):
                start, end = m.span()
                matched_str = text[start:end] if end <= len(text) else var
                
                match_obj = ProfanityMatch(
                    term=item.get("term", var),
                    category=category,
                    severity=severity,
                    matched_text=matched_str,
                    start=start,
                    end=end
                )
                matches.append(match_obj)
                
                if severity_order.get(severity, 0) > severity_order.get(highest_severity, 0):
                    highest_severity = severity

                # Mask in censored text
                for i in range(start, min(end, len(censored))):
                    censored[i] = "*"

    is_profane = len(matches) > 0
    return ProfanityResult(
        is_profane=is_profane,
        severity=highest_severity if is_profane else "none",
        matches=matches,
        censored_text="".join(censored)
    )

def is_profane(text: str) -> bool:
    """Quick boolean check if text contains Algerian profanity."""
    return detect_profanity(text).is_profane

def censor_profanity(text: str, mask: str = "***") -> str:
    """Replace profane substrings with mask."""
    result = detect_profanity(text)
    if not result.is_profane:
        return text
    # Replace contiguous sequences of asterisks with mask
    return re.sub(r'\*+', mask, result.censored_text)
