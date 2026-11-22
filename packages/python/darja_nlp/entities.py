"""Algerian entity extraction (Wilayas, Payment Methods, Prices)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional


_DATA_DIR = Path(__file__).parent / 'data'
_wilayas: Optional[List[Dict[str, Any]]] = None

PaymentMethodType = Literal['BARIDIMOB', 'EDAHABIA', 'CCP', 'COD']


@dataclass
class WilayaEntity:
    code: int
    code_str: str
    name_ar: str
    name_fr: str
    matched_text: str


@dataclass
class PaymentEntity:
    type: PaymentMethodType
    label: str
    matched_text: str


@dataclass
class PriceEntity:
    raw: str
    amount: Optional[float]
    currency: str = 'DZD'


@dataclass
class EntitiesResult:
    wilayas: List[WilayaEntity] = field(default_factory=list)
    payments: List[PaymentEntity] = field(default_factory=list)
    prices: List[PriceEntity] = field(default_factory=list)


def load_wilayas() -> List[Dict[str, Any]]:
    global _wilayas
    if _wilayas is not None:
        return _wilayas

    wilayas_path = _DATA_DIR / 'wilayas.json'
    with open(wilayas_path, 'r', encoding='utf-8') as f:
        _wilayas = json.load(f)
    return _wilayas


def get_wilayas() -> List[Dict[str, Any]]:
    """Return all 69 Algerian wilayas."""
    return load_wilayas()


def get_wilaya_by_code(code: int | str) -> Optional[Dict[str, Any]]:
    """Get wilaya details by numeric or string code."""
    wilayas = load_wilayas()
    num = int(code) if isinstance(code, str) else code
    for w in wilayas:
        if w['code'] == num:
            return w
    return None


_PAYMENT_PATTERNS = [
    (
        'BARIDIMOB',
        'BaridiMob (بريدي موب)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(baridimob|baridi\s*mob|بريدي\s*موب|بريديموب)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
    (
        'EDAHABIA',
        'Edahabia Card (البطاقة الذهبية)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(edahabia|dahabia|carte\s*edahabia|الذهبيه|الذهبية|بالذهبية|بالذهبيه|بطاقة\s*الذهبيه|بطاقه\s*الذهبيه|لاكارط\s*الذهبيه)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
    (
        'CCP',
        'CCP Postal Account (حساب بريدي)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(ccp|سي\s*سي\s*بي|حساب\s*بريدي|شيك\s*بريدي|virement\s*ccp)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
    (
        'COD',
        'Cash on Delivery (الدفع عند الاستلام)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(cod|cash\s*on\s*delivery|main\s*[aà]\s*main|الدفع\s*عند\s*الاستلام|كاش\s*عند\s*الاستلام|خلص\s*كي\s*تلحقك|كاش|يد\s*بيد)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
]

_PRICE_NUMERIC_PATTERN = re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(\d+(?:[.,]\d+)?)\s*(da|dzd|دج|دينار|الف|ألف|alf)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE)
_DARJA_AMOUNTS = [
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(مية\s*الف|100\s*الف|mya|myat\s*alf)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 1000.0),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(ميتين\s*الف|200\s*الف|mitin\s*alf)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 2000.0),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(خمسمية\s*الف|500\s*الف|khams\s*mya|500\s*alf)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 5000.0),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(مليون|mlyon|1\s*mlyon)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 10000.0),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(زوج\s*ملاين|2\s*mlyon|zoudj\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 20000.0),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(خمس\s*ملاين|5\s*mlyon|khams\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 50000.0),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(عشر\s*ملاين|10\s*mlyon|3achr\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 100000.0),
]


def _extract_wilayas(text: str, wilayas: List[Dict[str, Any]]) -> List[WilayaEntity]:
    results: List[WilayaEntity] = []
    added_codes: set[int] = set()
    lower_text = text.lower()

    # 1. Direct code patterns like "wilaya 16", "w 31", "l 16"
    code_regex = re.compile(r'\b(?:wilaya|w|ولاية|ولايه|l)\s*([0-6]?[0-9])\b', re.IGNORECASE)
    for code_match in code_regex.finditer(text):
        num = int(code_match.group(1))
        if 1 <= num <= 69 and num not in added_codes:
            w = next((item for item in wilayas if item['code'] == num), None)
            if w:
                added_codes.add(num)
                results.append(WilayaEntity(
                    code=w['code'],
                    code_str=w['code_str'],
                    name_ar=w['name_ar'],
                    name_fr=w['name_fr'],
                    matched_text=code_match.group(0),
                ))

    # 2. Name & Aliases matching
    for w in wilayas:
        if w['code'] in added_codes:
            continue

        candidates = [w['name_ar'], w['name_fr']] + w.get('aliases', [])
        for cand in candidates:
            if not cand or len(cand) < 2:
                continue
            cand_lower = cand.lower()
            escaped = re.escape(cand_lower)
            reg = re.compile(rf'(^|\s|[.,!?;:()]){escaped}($|\s|[.,!?;:()])', re.IGNORECASE)

            if reg.search(lower_text) or cand_lower in lower_text:
                if len(cand_lower) <= 3 and not reg.search(lower_text):
                    continue
                added_codes.add(w['code'])
                results.append(WilayaEntity(
                    code=w['code'],
                    code_str=w['code_str'],
                    name_ar=w['name_ar'],
                    name_fr=w['name_fr'],
                    matched_text=cand,
                ))
                break

    return results


def _extract_payments(text: str) -> List[PaymentEntity]:
    results: List[PaymentEntity] = []
    added_types: set[str] = set()

    for p_type, label, pattern in _PAYMENT_PATTERNS:
        match = pattern.search(text)
        if match and p_type not in added_types:
            added_types.add(p_type)
            results.append(PaymentEntity(
                type=p_type,  # type: ignore[arg-type]
                label=label,
                matched_text=match.group(0),
            ))

    return results


def _extract_prices(text: str) -> List[PriceEntity]:
    results: List[PriceEntity] = []

    # Match standard numbers with currency
    for match in _PRICE_NUMERIC_PATTERN.finditer(text):
        raw_val = match.group(1).replace(',', '.')
        unit = match.group(2).lower()
        val = float(raw_val)
        if unit in ('الف', 'ألف', 'alf'):
            val = val * 1000.0
        results.append(PriceEntity(
            raw=match.group(0),
            amount=val,
            currency='DZD',
        ))

    # Match Darja colloquial amounts
    for pattern, val in _DARJA_AMOUNTS:
        match = pattern.search(text)
        if match:
            results.append(PriceEntity(
                raw=match.group(0),
                amount=val,
                currency='DZD',
            ))

    return results


def extract_entities(text: str) -> EntitiesResult:
    """Extract Algerian Wilayas, Payment Methods, and Prices from text."""
    if not text:
        return EntitiesResult()

    wilayas = load_wilayas()
    return EntitiesResult(
        wilayas=_extract_wilayas(text, wilayas),
        payments=_extract_payments(text),
        prices=_extract_prices(text),
    )
