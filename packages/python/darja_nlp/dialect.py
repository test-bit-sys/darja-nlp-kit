"""Algerian regional dialect identification."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from .stopwords import tokenize


DialectRegion = Literal['WEST', 'EAST', 'CENTER', 'SOUTH', 'GENERAL_DARJA']

_DATA_DIR = Path(__file__).parent / 'data'
_dialects_data: Optional[Dict[str, Any]] = None


def _load_dialects_json() -> Dict[str, Any]:
    global _dialects_data
    if _dialects_data is not None:
        return _dialects_data
    json_path = _DATA_DIR / 'dialects.json'
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                _dialects_data = json.load(f)
                return _dialects_data
        except Exception:
            pass
    _dialects_data = {'regions': {}}
    return _dialects_data


REGIONAL_MARKERS: Dict[str, List[str]] = {
    'WEST': [
        'شوالا', 'شاكاين', 'شا', 'غايا', 'باغي', 'حرز', 'راك عاقل',
        'شراكم', 'كيراك', 'كيراكم', 'درك', 'حشمان', 'طاير', 'صايي',
        'طليت', 'تالمون', 'بلا مزية', 'نوليلك', 'غادي',
        'chwala', 'chakayn', 'ghaya', 'baghi', 'kirak', 'kirakom', 'drk',
        'sayi', 'bla mziya', 'ghadi'
    ],
    'EAST': [
        'واشنهي', 'قداش', 'ياسر', 'ضرك', 'زي', 'باهي', 'علاشنهي',
        'واشبيك', 'كفاه', 'ضروك', 'سيرتا', 'بونة', 'عيشك', 'يعيشك',
        'على عيني', 'قندورة',
        '9dach', 'yaser', 'bahi', 'kach', '3aychek', 'wachnahi'
    ],
    'CENTER': [
        'واشنو', 'حكاية', 'دروك', 'هكدا', 'هكداك', 'حوايج', 'البهجة',
        'العاصمة', 'دزاير', 'تشوف', 'مريڤل', 'حطة', 'هبال', 'كاش ما تسحق',
        'رانا هنا', 'صحيت',
        'wachnou', 'hakda', 'hakdak', 'hwaiej', 'mreguel', 'mrigel', '7atta', 'hbal'
    ],
    'SOUTH': [
        'واه', 'لاه', 'حتة', 'سوف', 'ميزاب', 'غرداية', 'ادرار', 'بسكرة',
        'ورقلة', 'بشار', 'على الراس والعين', 'مرحب بيك', 'بارك الله فيك',
        'سومة زينة', 'واش حالك',
        'wah', 'lah', '7ata', 'mr7eb bik', 'zin'
    ],
}


def get_dialect_metadata(region: DialectRegion) -> Dict[str, Any]:
    """Retrieve extended metadata, tone guide, and greetings for an Algerian dialect region."""
    data = _load_dialects_json()
    regions = data.get('regions', {})
    if region in regions:
        return regions[region]
    return {
        'name_ar': region,
        'tone_guide': 'دارجة جزائرية عفوية ومحترمة.',
        'greetings': [],
        'closure': [],
        'markers': REGIONAL_MARKERS.get(region, []),
    }


@dataclass
class DialectResult:
    region: DialectRegion
    confidence: float
    detected_markers: List[str] = field(default_factory=list)



def _get_merged_markers() -> Dict[str, List[str]]:
    """Combine built-in regional markers with dynamically enriched dialects.json markers."""
    data = _load_dialects_json()
    regions_data = data.get('regions', {})
    merged: Dict[str, List[str]] = {}
    for region in ('WEST', 'EAST', 'CENTER', 'SOUTH'):
        seen = set()
        items: List[str] = []
        for m in REGIONAL_MARKERS.get(region, []) + regions_data.get(region, {}).get('markers', []):
            low = m.lower()
            if low not in seen:
                seen.add(low)
                items.append(m)
        merged[region] = items
    return merged


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
    token_set = set(tokens)
    padded_tokens = f" {' '.join(tokens)} "

    scores: Dict[str, List[str]] = {
        'WEST': [],
        'EAST': [],
        'CENTER': [],
        'SOUTH': [],
    }

    for region, markers in _get_merged_markers().items():
        for marker in markers:
            lower_marker = marker.lower().strip()
            if not lower_marker:
                continue
            if ' ' in lower_marker:
                if f' {lower_marker} ' in padded_tokens:
                    scores[region].append(marker)
            elif lower_marker in token_set:
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
