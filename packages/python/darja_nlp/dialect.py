"""Algerian regional dialect identification."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal

from .stopwords import tokenize


DialectRegion = Literal['WEST', 'EAST', 'CENTER', 'SOUTH', 'GENERAL_DARJA']

REGIONAL_MARKERS: Dict[str, List[str]] = {
    'WEST': [
        'شوالا', 'شاكاين', 'شا', 'غايا', 'باغي', 'حرز', 'راك عاقل',
        'شراكم', 'كيراك', 'كيراكم', 'درك', 'حشمان', 'طاير',
        'chwala', 'chakayn', 'ghaya', 'baghi', 'kirak', 'kirakom', 'drk'
    ],
    'EAST': [
        'واشنهي', 'قداش', 'ياسر', 'ضرك', 'زي', 'باهي', 'علاشنهي',
        'واشبيك', 'كفاه', 'ضروك', 'سيرتا', 'بونة',
        '9dach', 'yaser', 'bahi', 'kach'
    ],
    'CENTER': [
        'واشنو', 'حكاية', 'دروك', 'هكدا', 'هكداك', 'حوايج', 'البهجة',
        'العاصمة', 'دزاير', 'تشوف',
        'wachnou', 'hakda', 'hakdak', 'hwaiej'
    ],
    'SOUTH': [
        'واه', 'لاه', 'حتة', 'سوف', 'ميزاب', 'غرداية', 'ادرار',
        'wah', 'lah', '7ata'
    ],
}


@dataclass
class DialectResult:
    region: DialectRegion
    confidence: float
    detected_markers: List[str] = field(default_factory=list)


def detect_dialect(text: str) -> DialectResult:
    """Identify Algerian regional dialect (WEST, EAST, CENTER, SOUTH, or GENERAL_DARJA)."""
    if not text:
        return DialectResult(
            region='GENERAL_DARJA',
            confidence=0.0,
            detected_markers=[],
        )

    tok_result = tokenize(text)
    tokens = [t.lower() for t in tok_result.tokens]
    lower_text = text.lower()

    scores: Dict[str, List[str]] = {
        'WEST': [],
        'EAST': [],
        'CENTER': [],
        'SOUTH': [],
    }

    for region, markers in REGIONAL_MARKERS.items():
        for marker in markers:
            lower_marker = marker.lower()
            if lower_marker in tokens or lower_marker in lower_text:
                scores[region].append(marker)

    top_region: DialectRegion = 'GENERAL_DARJA'
    max_count = 0
    all_detected: List[str] = []

    for reg, matches in scores.items():
        if len(matches) > max_count:
            max_count = len(matches)
            top_region = reg  # type: ignore[assignment]
            all_detected = matches

    if max_count == 0:
        return DialectResult(
            region='GENERAL_DARJA',
            confidence=0.5,
            detected_markers=[],
        )

    confidence = min(0.99, round((0.6 + max_count * 0.15) * 100) / 100)

    return DialectResult(
        region=top_region,
        confidence=confidence,
        detected_markers=all_detected,
    )
