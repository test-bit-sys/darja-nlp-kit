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
DeliveryCompanyType = Literal['YALIDINE', 'ZR_EXPRESS', 'MAYSTRO', 'PROCOLIS', 'EMS', 'KAZITOUR', 'GUEPEX']
DeliveryModeType = Literal['STOP_DESK', 'HOME_DELIVERY']


@dataclass
class WilayaEntity:
    code: int
    code_str: str
    name_ar: str
    name_fr: str
    matched_text: str
    commune: Optional[str] = None


@dataclass
class PaymentEntity:
    type: PaymentMethodType
    label: str
    matched_text: str


@dataclass
class DeliveryEntity:
    company: DeliveryCompanyType
    label: str
    matched_text: str


@dataclass
class DeliveryModeEntity:
    mode: DeliveryModeType
    label: str
    matched_text: str


@dataclass
class PhoneEntity:
    raw: str
    normalized: str


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
    deliveries: List[DeliveryEntity] = field(default_factory=list)
    delivery_mode: Optional[DeliveryModeEntity] = None
    phones: List[PhoneEntity] = field(default_factory=list)


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

_DELIVERY_COMPANY_PATTERNS = [
    (
        'YALIDINE',
        'Yalidine Express (ياليدين)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(yalidine|yalidin|ياليدين)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
    (
        'ZR_EXPRESS',
        'ZR Express (زد ار اكسبرس)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(zr\s*express|zr|زد\s*ار\s*اكسبرس|زد\s*ار)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
    (
        'MAYSTRO',
        'Maystro Delivery (مايسترو)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(maystro\s*delivery|maystro|مايسترو)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
    (
        'PROCOLIS',
        'Procolis (بروكولي)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(procolis|pro\s*colis|بروكولي|بروكوليس)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
    (
        'EMS',
        'EMS Algérie Poste (البريد السريع)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(ems|ems\s*algerie|البريد\s*السريع)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
    (
        'KAZITOUR',
        'Kazitour Express (كازيتور)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(kazitour|kazi\s*tour|كازيتور)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
    (
        'GUEPEX',
        'Guepex Express (قيباكس)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(guepex|قيباكس)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
]

_DELIVERY_MODE_PATTERNS = [
    (
        'STOP_DESK',
        'Stop Desk (استلام من المكتب)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(stop\s*desk|stopdesk|سطوب\s*ديسك|ستوب\s*ديسك|المكتب|فالبيرو|في\s*البيرو|agence)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
    (
        'HOME_DELIVERY',
        'Home Delivery (توصيل للمنزل)',
        re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(a\s*domicile|[aà]\s*domicile|للدار|لباب\s*الدار|توصيل\s*للمنزل|توصيل\s*للدار|فالدار)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE),
    ),
]

_PHONE_PATTERN = re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])((?:\+213|00213|0)\s*(?:[5-7]|2[0-9]|3[0-9]|4[0-9])(?:[\s.-]?\d){8})(?=$|\s|[^\w\u0600-\u06FF])')

_DARJA_MILLIONS_WORDS: Dict[str, float] = {
    'زوج': 2.0, 'تلات': 3.0, 'تلاتة': 3.0, 'ربع': 4.0, 'ربعة': 4.0,
    'خمس': 5.0, 'خمسة': 5.0, 'ست': 6.0, 'ستة': 6.0, 'سبع': 7.0,
    'سبعة': 7.0, 'تمن': 8.0, 'تمنية': 8.0, 'تسع': 9.0, 'تسعة': 9.0,
    'عشر': 10.0, 'عشرة': 10.0,
    'zouj': 2.0, 'zoudj': 2.0, 'tlata': 3.0, 'tleta': 3.0, 'rab3a': 4.0, 'reb3a': 4.0,
    'khamsa': 5.0, 'setta': 6.0, 'seb3a': 7.0, 'tmenya': 8.0, 'tes3a': 9.0, '3achra': 10.0,
}

_DARJA_THOUSANDS_WORDS: Dict[str, float] = {
    'مية': 100.0, 'ميتين': 200.0, 'تلمية': 300.0, 'تلتمية': 300.0, 'تلاتمية': 300.0,
    'ربعمية': 400.0, 'خمسمية': 500.0, 'ستمية': 600.0, 'سبعمية': 700.0, 'تمنمية': 800.0,
    'تسعمية': 900.0, 'عشرين': 20.0, 'تلاتين': 30.0, 'ربعين': 40.0, 'خمسين': 50.0,
    'ستين': 60.0, 'سبعين': 70.0, 'تمانين': 80.0, 'تسعين': 90.0,
    'mya': 100.0, 'myat': 100.0, 'mitin': 200.0, 'mitayn': 200.0, 'teltmya': 300.0,
    'rab3mya': 400.0, 'khamsmya': 500.0, 'settmya': 600.0, 'seb3mya': 700.0,
    'tmenmya': 800.0, 'tes3mya': 900.0, '3echrin': 20.0, 'tlatin': 30.0, 'rab3in': 40.0,
    'khamsin': 50.0, 'settin': 60.0, 'seb3in': 70.0, 'tmanin': 80.0, 'tes3in': 90.0,
}

_MILLIONS_MATCH_WORDS = r'زوج|تلات|تلاتة|ربع|ربعة|خمس|خمسة|ست|ستة|سبع|سبعة|تمن|تمنية|تسع|تسعة|عشر|عشرة|zouj|zoudj|tlata|tleta|rab3a|reb3a|khamsa|setta|seb3a|tmenya|tes3a|3achra'
_THOUSANDS_MATCH_WORDS = r'مية|ميتين|تلمية|تلتمية|تلاتمية|ربعمية|خمسمية|ستمية|سبعمية|تمنمية|تسعمية|عشرين|تلاتين|ربعين|خمسين|ستين|سبعين|تمانين|تسعين|mya|myat|mitin|mitayn|teltmya|rab3mya|khamsmya|settmya|seb3mya|tmenmya|tes3mya|3echrin|tlatin|rab3in|khamsin|settin|seb3in|tmanin|tes3in'

_COMPOUND_PRICE_PATTERN = re.compile(
    rf'(?:^|\s|[^\w\u0600-\u06FF])'
    rf'(\d+(?:[.,]\d+)?|{_MILLIONS_MATCH_WORDS})?\s*(?:ملاين|ملايين|مليون|mlyon|mlayen|mlayin)'
    rf'\s*(?:و|\+|et|w)\s*'
    rf'(\d+(?:[.,]\d+)?|{_THOUSANDS_MATCH_WORDS})?\s*(?:الف|ألف|alf)'
    rf'(?=$|\s|[^\w\u0600-\u06FF])',
    re.IGNORECASE,
)

_PRICE_NUMERIC_PATTERN = re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(\d+(?:[.,]\d+)?)\s*(da|dzd|دج|دينار|الف|ألف|alf)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE)
_DYNAMIC_MILLIONS_PATTERN = re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(\d+(?:[.,]\d+)?)\s*(?:ملاين|ملايين|مليون|mlyon|mlayen|mlayin)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE)
_DARJA_AMOUNTS = [
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(مية\s*الف|100\s*الف|mya|myat\s*alf)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 1000.0),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(ميتين\s*الف|200\s*الف|mitin\s*alf)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 2000.0),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(خمسمية\s*الف|500\s*الف|khams\s*mya|500\s*alf)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 5000.0),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(مليون|mlyon|1\s*mlyon)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 10000.0),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(زوج\s*ملاين|زوج\s*ملايين|zoudj\s*mlayen|zouj\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 20000.0),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(خمس\s*ملاين|khams\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 50000.0),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(عشر\s*ملاين|3achr\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 100000.0),
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
                all_communes = w.get('communes_sample', []) + w.get('communes_fr_sample', [])
                matched_com = next((c for c in all_communes if c.lower() == cand_lower), None)
                results.append(WilayaEntity(
                    code=w['code'],
                    code_str=w['code_str'],
                    name_ar=w['name_ar'],
                    name_fr=w['name_fr'],
                    matched_text=cand,
                    commune=matched_com,
                ))
                break

    # 3. Major Communes matching (550+ Algerian communes)
    for w in wilayas:
        if w['code'] in added_codes:
            continue

        communes = w.get('communes_sample', []) + w.get('communes_fr_sample', [])
        for com in communes:
            if not com or len(com) < 3:
                continue
            com_lower = com.lower()
            escaped = re.escape(com_lower)
            reg = re.compile(rf'(^|\s|[.,!?;:()]){escaped}($|\s|[.,!?;:()])', re.IGNORECASE)

            if reg.search(lower_text) or (len(com_lower) >= 4 and com_lower in lower_text):
                added_codes.add(w['code'])
                results.append(WilayaEntity(
                    code=w['code'],
                    code_str=w['code_str'],
                    name_ar=w['name_ar'],
                    name_fr=w['name_fr'],
                    matched_text=com,
                    commune=com,
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
    masked_text = text

    # 1. Match compound prices first (e.g. "زوج ملاين و خمسمية الف", "3 mlayen w 500 alf", "مليون وميتين الف")
    for match in _COMPOUND_PRICE_PATTERN.finditer(text):
        raw_m = match.group(1)
        raw_k = match.group(2)
        raw_full = match.group(0).strip()

        if not raw_m:
            millions_val = 1.0
        else:
            m_key = raw_m.lower()
            if m_key in _DARJA_MILLIONS_WORDS:
                millions_val = _DARJA_MILLIONS_WORDS[m_key]
            else:
                try:
                    millions_val = float(m_key.replace(',', '.'))
                except ValueError:
                    millions_val = 1.0

        if not raw_k:
            thousands_val = 1.0
        else:
            k_key = raw_k.lower()
            if k_key in _DARJA_THOUSANDS_WORDS:
                thousands_val = _DARJA_THOUSANDS_WORDS[k_key]
            else:
                try:
                    thousands_val = float(k_key.replace(',', '.'))
                except ValueError:
                    thousands_val = 0.0

        total_dzd = (millions_val * 10000.0) + (thousands_val * 10.0)
        results.append(PriceEntity(
            raw=raw_full,
            amount=total_dzd,
            currency='DZD',
        ))

        start, end = match.start(), match.end()
        masked_text = masked_text[:start] + (' ' * (end - start)) + masked_text[end:]

    # 2. Match standard numbers with currency on masked_text
    for match in _PRICE_NUMERIC_PATTERN.finditer(masked_text):
        raw_val = match.group(1).replace(',', '.')
        unit = match.group(2).lower()
        val = float(raw_val)
        if unit in ('الف', 'ألف', 'alf'):
            val = val * 1000.0
        results.append(PriceEntity(
            raw=match.group(0).strip(),
            amount=val,
            currency='DZD',
        ))
        start, end = match.start(), match.end()
        masked_text = masked_text[:start] + (' ' * (end - start)) + masked_text[end:]

    # 3. Match dynamic colloquial millions on masked_text
    for match in _DYNAMIC_MILLIONS_PATTERN.finditer(masked_text):
        raw_val = match.group(1).replace(',', '.')
        val = float(raw_val) * 10000.0
        results.append(PriceEntity(
            raw=match.group(0).strip(),
            amount=val,
            currency='DZD',
        ))
        start, end = match.start(), match.end()
        masked_text = masked_text[:start] + (' ' * (end - start)) + masked_text[end:]

    # 4. Match Darja fixed colloquial amounts on masked_text
    for pattern, val in _DARJA_AMOUNTS:
        match = pattern.search(masked_text)
        if match:
            results.append(PriceEntity(
                raw=match.group(0).strip(),
                amount=val,
                currency='DZD',
            ))
            start, end = match.start(), match.end()
            masked_text = masked_text[:start] + (' ' * (end - start)) + masked_text[end:]

    return results


def _extract_deliveries(text: str) -> List[DeliveryEntity]:
    results: List[DeliveryEntity] = []
    added: set[str] = set()

    for d_comp, label, pattern in _DELIVERY_COMPANY_PATTERNS:
        match = pattern.search(text)
        if match and d_comp not in added:
            added.add(d_comp)
            results.append(DeliveryEntity(
                company=d_comp,  # type: ignore[arg-type]
                label=label,
                matched_text=match.group(0).strip(),
            ))

    return results


def _extract_delivery_mode(text: str) -> Optional[DeliveryModeEntity]:
    for d_mode, label, pattern in _DELIVERY_MODE_PATTERNS:
        match = pattern.search(text)
        if match:
            return DeliveryModeEntity(
                mode=d_mode,  # type: ignore[arg-type]
                label=label,
                matched_text=match.group(0).strip(),
            )
    return None


def _extract_phones(text: str) -> List[PhoneEntity]:
    results: List[PhoneEntity] = []
    added_nums: set[str] = set()

    for match in _PHONE_PATTERN.finditer(text):
        raw_val = match.group(1).strip()
        cleaned = re.sub(r'[\s.-]', '', raw_val)
        if cleaned.startswith('00213'):
            cleaned = '0' + cleaned[5:]
        elif cleaned.startswith('+213'):
            cleaned = '0' + cleaned[4:]

        if cleaned not in added_nums:
            added_nums.add(cleaned)
            results.append(PhoneEntity(
                raw=raw_val,
                normalized=cleaned,
            ))

    return results


def extract_entities(text: str) -> EntitiesResult:
    """Extract Algerian Wilayas, Payment Methods, Prices, Deliveries, and Phones from text."""
    if not text:
        return EntitiesResult()

    wilayas = load_wilayas()
    return EntitiesResult(
        wilayas=_extract_wilayas(text, wilayas),
        payments=_extract_payments(text),
        prices=_extract_prices(text),
        deliveries=_extract_deliveries(text),
        delivery_mode=_extract_delivery_mode(text),
        phones=_extract_phones(text),
    )
