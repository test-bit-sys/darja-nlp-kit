"""
Human escalation and agent handoff detection for Algerian customer support.

Detects when an Algerian customer conversation requires human agent takeover,
such as extreme dissatisfaction, explicit requests for a human, or serious disputes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Literal, Optional, Tuple

EscalationUrgency = Literal['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NONE']
EscalationReason = Literal['ANGRY_CUSTOMER', 'HUMAN_REQUESTED', 'DISPUTE', 'LEGAL_THREAT']


@dataclass
class EscalationResult:
    needs_escalation: bool
    urgency: EscalationUrgency
    reason: Optional[EscalationReason] = None
    matched_triggers: List[str] = field(default_factory=list)
    guideline: str = ''


_HUMAN_REQUEST_TRIGGERS = [
    'احكي مع بنادم', 'مع انسان', 'مع بنادم', 'كاش انسان', 'عطيني المدير', 'خدمة الزبائن',
    'خدمة العملاء', 'عيطلي', 'كلمني', 'كلموني', 'حاب نهدر مع واحد', 'نهدر مع بنادم',
    'عيطولي في الهاتف', 'واحد يفهم', 'انسان حقيقي',
    'appel moi', 'appelez moi', 'parler a un responsable', 'parler a un agent',
    'service client', 'responsable', 'humain', '3aytli', 'nahdar m3a bnadm', 'telephonez moi',
]

_ANGRY_CUSTOMER_TRIGGERS = [
    'حشيتوهالي', 'حشاوها لي', 'سراقين', 'سرقة عيني عينك', 'فضيحة', 'رجعولي دراهمي',
    'وكيلكم ربي', 'حقارين', 'الله لا يربحكم', 'بهدلتو بينا', 'سلعة ميتة ومفاتشة',
    'تندمو', 'ما تحشموش', 'خردة', 'تبهديلة', 'سراق',
    '7chawhali', 'ser9a', 'arnaqueurs', 'la pire boutique', 'fdiha', 'behdeltouna',
    'rej3oli drahmi', 'ma thechmouch', 'voleurs',
]

_DISPUTE_TRIGGERS = [
    'ما رديتوش عليا', 'ما حبيتوش تبدلو', 'روتور مبلوكي', 'سلعة غالطة وما رديتوش',
    'عندي سمانة نستنى', 'عندي شهر', 'ما وصلني والو', 'دراهمي ما رجعوش',
    'pas de reponse', 'bloque', 'bloquer', '1 mois', 'une semaine',
]

_LEGAL_THREAT_TRIGGERS = [
    'نشكي بيكم', 'لابوليس', 'حماية المستهلك', 'العدالة', 'نديرلكم شكوى', 'محكمة',
    'la police', 'protection du consommateur', 'plainte', 'tribunal',
]


def detect_escalation(text: str) -> EscalationResult:
    """
    Analyze if customer message warrants immediate human support escalation.
    """
    if not text:
        return EscalationResult(needs_escalation=False, urgency='NONE', reason=None, matched_triggers=[], guideline='')

    lower = text.lower()

    # 1. Legal / Police Threat (CRITICAL)
    legal_matches = [t for t in _LEGAL_THREAT_TRIGGERS if t.lower() in lower]
    if legal_matches:
        return EscalationResult(
            needs_escalation=True,
            urgency='CRITICAL',
            reason='LEGAL_THREAT',
            matched_triggers=legal_matches,
            guideline='🚨 الزبون يهدد بمتابعة قانونية أو شكوى رسمية! يجب تحويل المحادثة فوراً للإدارة وتجنب أي جدال آلي.',
        )

    # 2. Angry Customer / Severe Abuse (HIGH)
    angry_matches = [t for t in _ANGRY_CUSTOMER_TRIGGERS if t.lower() in lower]
    if angry_matches:
        return EscalationResult(
            needs_escalation=True,
            urgency='HIGH',
            reason='ANGRY_CUSTOMER',
            matched_triggers=angry_matches,
            guideline='⚠️ الزبون غاضب جداً ويتهم المتجر بسوء النية أو السرقة. يجب تدخل عون بشري لامتصاص الغضب وتقديم تعويض/استرجاع.',
        )

    # 3. Explicit Request for Human (HIGH / MEDIUM)
    human_matches = [t for t in _HUMAN_REQUEST_TRIGGERS if t.lower() in lower]
    if human_matches:
        return EscalationResult(
            needs_escalation=True,
            urgency='HIGH',
            reason='HUMAN_REQUESTED',
            matched_triggers=human_matches,
            guideline='👤 الزبون يطلب التحدث مع شخص حقيقي أو مسؤول. تجنب الردود الآلية الطويلة وسهّل تواصل ممثل خدمة العملاء معه.',
        )

    # 4. Long-standing Dispute / No Response (MEDIUM)
    dispute_matches = [t for t in _DISPUTE_TRIGGERS if t.lower() in lower]
    if dispute_matches:
        return EscalationResult(
            needs_escalation=True,
            urgency='MEDIUM',
            reason='DISPUTE',
            matched_triggers=dispute_matches,
            guideline='📦 نزاع بخصوص تأخر كبير أو عدم استجابة في الاستبدال. يحتاج مراجعة بشرية لحالة الطلبية وشركة التوصيل.',
        )

    return EscalationResult(
        needs_escalation=False,
        urgency='NONE',
        reason=None,
        matched_triggers=[],
        guideline='محادثة طبيعية، يمكن لوكيل الذكاء الاصطناعي الرد عليها مباشرة.',
    )
