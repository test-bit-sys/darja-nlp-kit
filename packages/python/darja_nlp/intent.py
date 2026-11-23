"""
Intent classification for Algerian Darja e-commerce and customer communication.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Tuple

IntentType = Literal[
    'ORDER',
    'PRICE_INQUIRY',
    'AVAILABILITY_INQUIRY',
    'DELIVERY_INQUIRY',
    'COMPLAINT',
    'GREETING',
    'UNKNOWN',
]


@dataclass
class IntentResult:
    intent: IntentType
    confidence: float
    matched_keywords: List[str] = field(default_factory=list)


_INTENT_RULES: List[Tuple[IntentType, List[str]]] = [
    (
        'COMPLAINT',
        [
            'مكسرة', 'مكسر', 'ما وصلتش', 'ما لحقتش', 'روطار', 'سلعة عيانة', 'سلعة ميتة', 'حشيتوهالي',
            'حشاوها لي', 'بدلوهالي', 'روتور', 'رجعولي دراهمي', 'ما رديتوش', 'حقار', 'سراقين', 'سرقة',
            'فضيحة', 'سلعة مفاتشة', 'ماشي كيما الفوتو', 'ماشي كيما التصويرة', 'ناقصة', 'معطوبة', 'مخدوعة',
            'reclamation', 'retour', 'casse', 'mfetcha', 'retard', 'ma wesletch', '7chawhali',
            'arnaque', 'ser9a', 'khorda', 'naqsa'
        ]
    ),
    (
        'ORDER',
        [
            'كوموندي', 'نكوموندي', 'كومونديلي', 'كوموندالي', 'باغي نشري', 'راني باغي', 'باغي', 'حاب نشري',
            'حبيت نشري', 'راني حاب', 'حاب', 'حبيت', 'ابعثلي', 'ابعثهالي', 'ابعثوهالي', 'احجزلي', 'حجز', 'احجز',
            'راني شاري', 'نشريها', 'نشري', 'جيبهالي', 'حاب نطلب', 'طلب شراء', 'نحتاج حبة', 'نحتاج زوج', 'نحتاج',
            'commander', 'ncommander', 'baghi nchri', 'rani baghi', 'baghi', 'hab nchri', '7ab nchri',
            'rani hab', 'rani 7ab', 'hab', '7ab', 'habb', 'nchri', 'chrit', 'nchriha', 'nchrihoum',
            'ab3atli', 'ab3athali', 'livrili', 'livrihali', 'livreli', '7jezli', 'reserver', 'je veux acheter'
        ]
    ),
    (
        'DELIVERY_INQUIRY',
        [
            'شحال التوصيل', 'كاين توصيل', 'توصلو', 'توصيل لـ', 'توصيل', 'ليفريزون', 'شحال ليفريزون',
            'وقتاش تلحق', 'وقتاش يوصل', 'شحال تاخذ وقت', 'توصلوها', 'توصيل مجاني', 'شحال فالدار',
            'livraison', 'chhal livraison', 'toussil', 'twaslou', 'we9tach tel7a9', 'wektach telhaq',
            'chhal w9t', 'livraison gratuite', 'frais de livraison', 'delai'
        ]
    ),
    (
        'PRICE_INQUIRY',
        [
            'شحال', 'بشحال', 'بقداش', 'قداش', 'سومة', 'شحال السومة', 'شحال يدير', 'شحال دير',
            'شحال راها دير', 'بشحال هاذي', 'شحال تسوى', 'بري', 'بري تاعو', 'سعر', 'شحال السعر',
            'prix', 'bch7al', 'ch7al', 'bchhal', 'chhal', '9dach', 'qadach', 'souma', 'c combien',
            'combien', 'chhal ydir', 'chhal tdir', 'ch7al ydir', 'tarif'
        ]
    ),
    (
        'AVAILABILITY_INQUIRY',
        [
            'كاينة', 'كاين', 'كاينين', 'متوفرة', 'متوفر', 'مازالت', 'مازال كاين', 'مازال كاينة',
            'ديسبو', 'مازالت عندكم', 'عندكم منها', 'كاش ما بقا', 'كاش جديد', 'كاين ستوك',
            'kayen', 'kayna', 'dispo', 'disponible', 'mazal', 'mazal kayn', 'mazal kayna', '3andkom',
            'fih stock'
        ]
    ),
    (
        'GREETING',
        [
            'سلام', 'سلام عليكم', 'السلام عليكم', 'صباح الخير', 'مساء الخير', 'يعطيك الصحة', 'صحيت',
            'واش راك', 'كيراك', 'كيراكم', 'شراكم', 'واش خويا', 'عيشك', 'خويا لعزيز', 'ربي يحفظك',
            'salam', 'slm', 'salam alikoum', 'sbah lkhir', 'msa lkhir', 'sahit', 'kirak', 'wach rak',
            'azul', 'bonjour', 'bonsoir'
        ]
    ),
]


def identify_intent(text: str) -> IntentResult:
    """
    Identify user intent (ORDER, PRICE_INQUIRY, AVAILABILITY_INQUIRY,
    DELIVERY_INQUIRY, COMPLAINT, GREETING, or UNKNOWN).
    """
    if not text:
        return IntentResult(intent='UNKNOWN', confidence=0.0, matched_keywords=[])

    lower_text = text.lower()
    scores: Dict[IntentType, List[str]] = {
        'COMPLAINT': [],
        'ORDER': [],
        'DELIVERY_INQUIRY': [],
        'PRICE_INQUIRY': [],
        'AVAILABILITY_INQUIRY': [],
        'GREETING': [],
    }

    for intent, keywords in _INTENT_RULES:
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in lower_text:
                scores[intent].append(kw)

    # Priority order for operational/business intents:
    # COMPLAINT > ORDER > DELIVERY_INQUIRY > PRICE_INQUIRY > AVAILABILITY_INQUIRY
    business_priority: List[IntentType] = [
        'COMPLAINT',
        'ORDER',
        'DELIVERY_INQUIRY',
        'PRICE_INQUIRY',
        'AVAILABILITY_INQUIRY',
    ]

    best_intent: IntentType = 'UNKNOWN'
    best_keywords: List[str] = []

    for intent in business_priority:
        kws = scores[intent]
        if len(kws) > 0:
            best_intent = intent
            best_keywords = kws
            break

    # Fallback to GREETING only if no operational business intent was expressed
    if best_intent == 'UNKNOWN' and len(scores['GREETING']) > 0:
        best_intent = 'GREETING'
        best_keywords = scores['GREETING']

    if best_intent == 'UNKNOWN':
        return IntentResult(intent='UNKNOWN', confidence=0.0, matched_keywords=[])

    confidence = min(0.99, round(0.70 + (len(best_keywords) * 0.1), 2))
    return IntentResult(
        intent=best_intent,
        confidence=confidence,
        matched_keywords=best_keywords,
    )
