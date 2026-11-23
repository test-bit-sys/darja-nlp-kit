"""
Quantity and product attribute extraction for Algerian Darja e-commerce.

Extracts colloquial quantities (e.g., حبة، زوج، 3 حبات، شكارة، باكية، كردونة، دوزينة)
and product attributes like colors and clothing/footwear sizes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union


@dataclass
class QuantityEntity:
    raw: str
    value: Union[int, float]
    unit: str


@dataclass
class ProductAttributes:
    colors: List[str] = field(default_factory=list)
    sizes: List[str] = field(default_factory=list)


_UNIT_NUMBER_WORDS: Dict[str, float] = {
    'زوج': 2.0,
    'تلات': 3.0,
    'تلاتة': 3.0,
    'ربع': 4.0,
    'ربعة': 4.0,
    'خمس': 5.0,
    'خمسة': 5.0,
    'ست': 6.0,
    'ستة': 6.0,
    'سبع': 7.0,
    'سبعة': 7.0,
    'تمن': 8.0,
    'تمنية': 8.0,
    'تسع': 9.0,
    'تسعة': 9.0,
    'عشر': 10.0,
    'عشرة': 10.0,
    'zouj': 2.0,
    'zoudj': 2.0,
    'tlata': 3.0,
    'tleta': 3.0,
    'rab3a': 4.0,
    'khamsa': 5.0,
    'setta': 6.0,
    'seb3a': 7.0,
    'tmenya': 8.0,
    'tes3a': 9.0,
    '3achra': 10.0,
}

# Fixed Darja units with predefined counts (e.g. دوزينة = 12)
_FIXED_QUANTITY_PATTERNS: List[Tuple[re.Pattern, float, str]] = [
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(دوزينة|دزينة|douzina|douzaine)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 12.0, 'دوزينة'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(زوج\s*دوزينات|2\s*douzina)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 24.0, 'دوزينة'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(حبة\s*وحدة|حبة|حبه|1\s*hba|hba|7ba)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 1.0, 'حبة'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(شكارة|chkara|1\s*chkara)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 1.0, 'شكارة'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(باكية|باكيه|bakya|1\s*boite|boite)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 1.0, 'باكية'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF])(كرطونة|كردونة|carton|1\s*carton)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 1.0, 'كرطونة'),
]

_NUM_WORDS_STR = r'زوج|تلات|تلاتة|ربع|ربعة|خمس|خمسة|ست|ستة|سبع|سبعة|تمن|تمنية|تسع|تسعة|عشر|عشرة|zouj|zoudj|tlata|tleta|rab3a|khamsa|setta|seb3a|tmenya|tes3a|3achra'
_UNITS_STR = r'حبات|حبة|حبه|شكاير|شكارة|باكيات|باكية|كراتن|كراطن|كرطونة|كردونة|صاشيات|صاشي|hbat|7bat|chkayer|bakyat|cartons|boites'

_DYNAMIC_QUANTITY_PATTERN = re.compile(
    rf'(?:^|\s|[^\w\u0600-\u06FF])(\d+(?:\.\d+)?|{_NUM_WORDS_STR})\s*({_UNITS_STR})(?=$|\s|[^\w\u0600-\u06FF])',
    re.IGNORECASE,
)

_COLORS_MAP: List[Tuple[re.Pattern, str]] = [
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(كحل|كحلة|كحلين|noir|noire|noires|k7al|ke7la)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'كحل / noir'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(بيض|بيضا|بيضاء|بيوضة|blanc|blanche|byad|bida)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'بيض / blanc'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(بيج|beige)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'بيج / beige'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(غوج|أحمر|احمر|حمرا|حمراء|rouge|7mar|7amra)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'غوج / rouge'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(مارون|قهوي|قهوية|marron|maron|9ahwi)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'مارون / marron'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(خضر|خضرا|خضراء|vert|verte|khdar|khadra)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'خضر / vert'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(غري|رمادي|رمادية|gris|grise)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'غري / gris'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(كحلي|بلو نوي|bleu\s*nuit|bleu\s*marine)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'كحلي / bleu nuit'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(بلو|أزرق|ازرق|زرقة|زرقاء|bleu|bleue|zra9)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'بلو / bleu'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(دوري|ذهبي|ذهبية|dore|doré|dorée)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'دوري / doré'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(أرجونتي|ارجونتي|فضي|فضية|argente|argenté)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'ارجونتي / argenté'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(روز|وردي|وردية|rose)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'روز / rose'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(موف|بنفسجي|violet|mauve)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'موف / mauve'),
    (re.compile(r'(?:^|\s|[^\w\u0600-\u06FF]|و)(سيل|بلو سيل|bleu\s*ciel)(?=$|\s|[^\w\u0600-\u06FF])', re.IGNORECASE), 'سيل / bleu ciel'),
]

_CLOTHING_SIZES = [
    re.compile(r'\b(xxxl|3xl)\b', re.IGNORECASE),
    re.compile(r'\b(xxl|2xl)\b', re.IGNORECASE),
    re.compile(r'\b(xl)\b', re.IGNORECASE),
    re.compile(r'\b(l)\b', re.IGNORECASE),
    re.compile(r'\b(m)\b', re.IGNORECASE),
    re.compile(r'\b(s)\b', re.IGNORECASE),
    re.compile(r'\b(xs)\b', re.IGNORECASE),
]

_SHOE_SIZE_PATTERN = re.compile(
    r'(?:pointure|taille|مقاس|نمرة|la\s*taille|pntr)?\s*([3-4][0-9])\b',
    re.IGNORECASE,
)


def extract_quantities(text: str) -> List[QuantityEntity]:
    """Extract Algerian colloquial and numeric quantities with units."""
    if not text:
        return []

    results: List[QuantityEntity] = []
    masked = text

    # 1. Dynamic matching (e.g. "3 حبات", "زوج شكاير", "5 cartons", "2 hbat")
    for match in _DYNAMIC_QUANTITY_PATTERN.finditer(text):
        raw_num = match.group(1).lower()
        raw_unit = match.group(2).lower()
        raw_full = match.group(0).strip()

        if raw_num in _UNIT_NUMBER_WORDS:
            val = _UNIT_NUMBER_WORDS[raw_num]
        else:
            try:
                val = float(raw_num.replace(',', '.'))
            except ValueError:
                val = 1.0

        unit_norm = raw_unit
        if raw_unit in ('حبات', 'hbat', '7bat'):
            unit_norm = 'حبة'
        elif raw_unit in ('شكاير', 'chkayer'):
            unit_norm = 'شكارة'
        elif raw_unit in ('باكيات', 'bakyat', 'boites'):
            unit_norm = 'باكية'
        elif raw_unit in ('كراتن', 'كراطن', 'cartons'):
            unit_norm = 'كرطونة'
        elif raw_unit in ('صاشيات',):
            unit_norm = 'صاشي'

        final_val = int(val) if val == int(val) else val
        results.append(QuantityEntity(
            raw=raw_full,
            value=final_val,
            unit=unit_norm,
        ))
        start, end = match.start(), match.end()
        masked = masked[:start] + (' ' * (end - start)) + masked[end:]

    # 2. Fixed units (e.g. "دوزينة", "شكارة", "حبة") on masked text
    for pattern, val, unit in _FIXED_QUANTITY_PATTERNS:
        match = pattern.search(masked)
        if match:
            final_val = int(val) if val == int(val) else val
            results.append(QuantityEntity(
                raw=match.group(0).strip(),
                value=final_val,
                unit=unit,
            ))
            start, end = match.start(), match.end()
            masked = masked[:start] + (' ' * (end - start)) + masked[end:]

    return results


def extract_product_attributes(text: str) -> ProductAttributes:
    """Extract product colors and sizes (clothing S-XXL, shoe sizes 36-46)."""
    if not text:
        return ProductAttributes()

    colors: List[str] = []
    added_colors: set[str] = set()

    for pattern, label in _COLORS_MAP:
        if pattern.search(text) and label not in added_colors:
            added_colors.add(label)
            colors.append(label)

    sizes: List[str] = []
    added_sizes: set[str] = set()

    # Shoe sizes (36 to 46)
    for match in _SHOE_SIZE_PATTERN.finditer(text):
        val_str = match.group(1)
        num = int(val_str)
        if 35 <= num <= 48 and val_str not in added_sizes:
            added_sizes.add(val_str)
            sizes.append(val_str)

    # Clothing sizes (XS to 3XL)
    for pat in _CLOTHING_SIZES:
        match = pat.search(text)
        if match:
            s_val = match.group(1).upper()
            if s_val not in added_sizes:
                added_sizes.add(s_val)
                sizes.append(s_val)

    return ProductAttributes(colors=colors, sizes=sizes)
