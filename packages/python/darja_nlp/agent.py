"""
AI Agent integration module for Algerian Darja communication.

Enables LLMs (GPT-4o, Gemini, Claude, Llama, Mistral) to understand and reply
in authentic Algerian Darja like a human merchant/representative.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from .normalizer import normalize
from .arabizi import arabizi_to_arabic
from .sentiment import analyze_sentiment
from .entities import extract_entities, get_wilaya_by_code
from .dialect import detect_dialect
from .intent import identify_intent, IntentType
from .escalation import detect_escalation

_DATA_DIR = Path(__file__).parent / 'data'
_dialogues_cache: Optional[List[Dict[str, Any]]] = None


def _load_dialogues() -> List[Dict[str, Any]]:
    global _dialogues_cache
    if _dialogues_cache is not None:
        return _dialogues_cache
    dialogues_path = _DATA_DIR / 'dialogues.json'
    if dialogues_path.exists():
        try:
            with open(dialogues_path, 'r', encoding='utf-8') as f:
                _dialogues_cache = json.load(f)
                return _dialogues_cache
        except Exception:
            pass
    _dialogues_cache = []
    return _dialogues_cache


def get_few_shot_dialogues(
    region: str = "GENERAL_DARJA",
    intent: Optional[str] = None,
    limit: int = 2
) -> List[Dict[str, Any]]:
    """
    Retrieve real Algerian dialogue exchanges matching the customer's dialect region
    and/or intent to serve as grounding few-shot examples for LLMs.
    """
    all_dialogues = _load_dialogues()
    if not all_dialogues:
        return []

    # Filter by region
    region_upper = region.upper()
    regional = [d for d in all_dialogues if d.get('region', '').upper() == region_upper]
    if not regional:
        regional = [d for d in all_dialogues if d.get('region', '').upper() == 'GENERAL_DARJA']

    # Filter or prioritize by intent if provided
    selected: List[Dict[str, Any]] = []
    if intent and intent.upper() != "UNKNOWN":
        intent_upper = intent.upper()
        matching_intent = [d for d in regional if d.get('intent', '').upper() == intent_upper]
        selected.extend(matching_intent[:limit])

    # If we need more to reach limit, fill with other regional dialogues
    for d in regional:
        if len(selected) >= limit:
            break
        if d not in selected:
            selected.append(d)

    # Fallback to general if still below limit
    if len(selected) < limit:
        for d in all_dialogues:
            if len(selected) >= limit:
                break
            if d not in selected:
                selected.append(d)

    return [
        {
            "id": d.get("id"),
            "region": d.get("region"),
            "intent": d.get("intent"),
            "customer_message": d.get("customer_message"),
            "merchant_response": d.get("merchant_response"),
        }
        for d in selected[:limit]
    ]


INTENT_GUIDELINES: Dict[str, str] = {
    'ORDER': '🛒 نية الزبون: طلب شراء/حجز. اطلب منه تأكيد الاسم، الولاية/البلدية، ورقم الهاتف لتسجيل طلبيته فورا.',
    'PRICE_INQUIRY': '💰 نية الزبون: استفسار عن السعر. أعطه السعر بالدينار الجزائري مع توضيح مصاريف التوصيل.',
    'AVAILABILITY_INQUIRY': '📦 نية الزبون: توفر السلعة. أكد التوفر وحفزه على الطلب فورا.',
    'DELIVERY_INQUIRY': '🚚 نية الزبون: التوصيل والشحن. وضح سعر ومدة التوصيل لولايته (خدمة سريعة للدار أو المكتب).',
    'COMPLAINT': '⚠️ نية الزبون: شكوى أو استرجاع. استوعب غضب الزبون بلطف واعتذر وقم بحل الإشكال باحترافية.',
    'GREETING': '👋 نية الزبون: تحية وتواصل. رد بترحيب جزائري عفوي ومستعد للخدمة.',
    'UNKNOWN': 'استفسار عام. قدم المساعدة بطريقة واضحة ومباشرة.',
}

DIALECT_GUIDELINES: Dict[str, str] = {
    "WEST": "لهجة الغرب الجزائري (وهران وتلمسان): استعمل كلمات خفيفة مثل (درك، غايا، مرحبا بيك خويا، ما تقلقش روحك).",
    "EAST": "لهجة الشرق الجزائري (قسنطينة وسطيف وعنابة): استعمل كلمات دافئة مثل (عيشك، ضرك، وشبيك، على عيني، ما كاش مشكل).",
    "CENTER": "لهجة الوسط والعاصمة (الجزائر والبليدة): استعمل أسلوب العاصمة السلس (واش خويا، مرحبا بيك، رانا هنا، كاش ما تسحق).",
    "SOUTH": "لهجة الجنوب الجزائري الكريمة: استعمل كلمات الترحيب والأصالة (مرحبا بيك، ربي يحفظك، على راسنا وعينينا).",
    "GENERAL_DARJA": "دارجة جزائرية عامة ومفهومة ومحترمة تجمع بين العفوية واللباقة المهنية."
}


def build_agent_context(message: str, store_name: str = "Bazar El Djazair") -> Dict[str, Any]:
    """
    Process a raw Algerian message and build a structured, ground-truth context
    for AI agents and LLMs.
    """
    raw_message = message or ""
    arabic_trans = arabizi_to_arabic(raw_message)
    normalized = normalize(raw_message)

    # Intent, dialect, sentiment, escalation, and entity extraction
    intent = identify_intent(raw_message)
    escalation = detect_escalation(raw_message)
    dialect = detect_dialect(raw_message)
    sentiment = analyze_sentiment(raw_message)
    entities = extract_entities(raw_message)

    # Tone recommendation based on escalation & sentiment
    if escalation.needs_escalation:
        tone = "CRITICAL_ESCALATION"
        tone_instruction = f"🚨 تصعيد فوري: {escalation.guideline}"
    elif sentiment.label == "NEGATIVE":
        tone = "APOLOGETIC_AND_REASSURING"
        tone_instruction = "⚠️ الزبون غاضب أو يشتكي! ابدأ بتطييب الخاطر والاعتذار ('حقك علينا خويا، ما تقلقش، المشكل نحلوه درك'). تجنب الجفاف والردود الآلية."
    elif sentiment.label == "POSITIVE":
        tone = "WARM_AND_CELEBRATING"
        tone_instruction = "😊 الزبون مسرور وراضٍ. رد بابتماس وترحاب حار ('ربي يحفظك، شهادة نعتزوا بيها، سلعة لوز لزبائننا')."
    else:
        tone = "PROFESSIONAL_HELPFUL"
        tone_instruction = "🤝 الزبون يستفسر. أجب بوضوح وسرعة ومهنية جزائرية عفوية."

    wilayas_summary = []
    for w in entities.wilayas:
        commune_info = f" - بلدية {w.commune}" if w.commune else ""
        wilayas_summary.append(f"{w.name_ar} ({w.code_str}){commune_info}")

    payments_summary = [p.label for p in entities.payments]
    prices_summary = [f"{p.amount:,.0f} دج ({p.raw})" for p in entities.prices if p.amount is not None]
    deliveries_summary = [d.label for d in entities.deliveries]
    delivery_mode_summary = entities.delivery_mode.label if entities.delivery_mode else None
    phones_summary = [
        f"{ph.normalized} ({ph.operator_label})" if ph.operator_label else ph.normalized
        for ph in entities.phones
    ]
    quantities_summary = [f"{q.value} {q.unit} ({q.raw})" for q in (entities.quantities or [])]
    product_attributes_summary = {
        "colors": entities.attributes.colors if entities.attributes else [],
        "sizes": entities.attributes.sizes if entities.attributes else [],
    }

    return {
        "store_name": store_name,
        "raw_message": raw_message,
        "arabic_transliterated": arabic_trans,
        "normalized": normalized,
        "intent": {
            "intent": intent.intent,
            "confidence": intent.confidence,
            "matched_keywords": intent.matched_keywords,
            "guideline": INTENT_GUIDELINES.get(intent.intent, INTENT_GUIDELINES["UNKNOWN"]),
        },
        "escalation": {
            "needs_escalation": escalation.needs_escalation,
            "reason": escalation.reason,
            "urgency": escalation.urgency,
            "matched_triggers": escalation.matched_triggers,
            "guideline": escalation.guideline,
        },
        "dialect": {
            "region": dialect.region,
            "confidence": dialect.confidence,
            "detected_markers": dialect.detected_markers,
            "guideline": DIALECT_GUIDELINES.get(dialect.region, DIALECT_GUIDELINES["GENERAL_DARJA"]),
        },
        "sentiment": {
            "label": sentiment.label,
            "score": sentiment.score,
            "tone": tone,
            "tone_instruction": tone_instruction,
        },
        "grounded_facts": {
            "wilayas": wilayas_summary,
            "payments": payments_summary,
            "prices_dzd": prices_summary,
            "delivery_companies": deliveries_summary,
            "delivery_mode": delivery_mode_summary,
            "phones": phones_summary,
            "quantities": quantities_summary,
            "product_attributes": product_attributes_summary,
        },
        "few_shot_examples": get_few_shot_dialogues(
            region=dialect.region,
            intent=intent.intent,
            limit=2
        ),
    }


def format_agent_system_prompt(context: Dict[str, Any]) -> str:
    """Format a system prompt for an LLM based on extracted agent context."""
    store = context.get("store_name", "المتجر")
    intent = context.get("intent", {"intent": "UNKNOWN", "guideline": "استفسار عام."})
    escalation = context.get("escalation", {"needs_escalation": False, "reason": "NONE", "urgency": "LOW", "guideline": ""})
    dialect = context["dialect"]
    sentiment = context["sentiment"]
    facts = context["groundedFacts"] if "groundedFacts" in context else context["grounded_facts"]

    escalation_notice = ""
    needs_esc = escalation.get("needs_escalation") or escalation.get("needsEscalation")
    if needs_esc:
        reason = escalation.get("reason", "")
        urgency = escalation.get("urgency", "")
        guideline = escalation.get("guideline", "")
        escalation_notice = f"\n🚨 [تنبيه تصعيد عاجل - Escalation Triggered]:\n- السبب: {reason} (درجة الإلحاح: {urgency})\n- الإجراء: {guideline}\n"

    quantities_list = facts.get("quantities", [])
    quantities_str = ", ".join(quantities_list) if quantities_list else "غير محددة"

    prod_attrs = facts.get("product_attributes") or facts.get("productAttributes") or {}
    colors_list = prod_attrs.get("colors", [])
    sizes_list = prod_attrs.get("sizes", [])
    colors_str = ", ".join(colors_list) if colors_list else "غير محدد"
    sizes_str = ", ".join(sizes_list) if sizes_list else "غير محدد"

    few_shots = context.get("few_shot_examples") or context.get("fewShotExamples") or []
    few_shots_section = ""
    if few_shots:
        few_shots_section = "\n[أمثلة واقعية لنبرة الرد بالدارجة الجزائرية المستهدفة]:\n"
        for i, ex in enumerate(few_shots, 1):
            few_shots_section += f"{i}. رسالة الزبون: \"{ex['customer_message']}\"\n   رد التاجر الطبيعي: \"{ex['merchant_response']}\"\n"

    prompt = f"""أنت مساعد خدمة عملاء ذكي وبشري جداً لمتجر إلكتروني جزائري '{store}'.
مهمتك الرد على الزبون الجزائري بدارجة واقعية ومتقنة 100%، كأنك تاجر جزائري محترف ولطيف.{escalation_notice}
[السياق المستخرج من رسالة الزبون]:
- الرسالة: "{context['raw_message']}"
- الترجمة التفسيرية (إذا كانت عربيزي): "{context['arabic_transliterated']}"
- النية الأساسية (Intent): {intent['intent']} ({intent['guideline']})
- المنطقة الجغرافية للهجة: {dialect['region']} ({dialect['guideline']})
- حالة الزبون النفسية: {sentiment['label']} (الدرجة: {sentiment['score']})
- إرشادات النبرة: {sentiment['tone_instruction']}
- الولايات والبلديات: {', '.join(facts['wilayas']) if facts['wilayas'] else 'غير محددة'}
- الكمية المطلوبة: {quantities_str}
- مواصفات المنتج (ألوان/مقاسات): ألوان: {colors_str} | مقاسات: {sizes_str}
- المبالغ المذكورة بالدينار: {', '.join(facts['prices_dzd']) if facts['prices_dzd'] else 'غير محددة'}
- وسائل الدفع المرصودة: {', '.join(facts['payments']) if facts['payments'] else 'غير محددة'}
- شركات التوصيل: {', '.join(facts['delivery_companies']) if facts['delivery_companies'] else 'غير محددة'}
- نمط التوصيل: {facts['delivery_mode'] if facts['delivery_mode'] else 'غير محدد'}
- أرقام الهاتف: {', '.join(facts['phones']) if facts['phones'] else 'غير متوفرة'}
{few_shots_section}
[قواعد صارمة للرد]:
1. تحدث بدارجة جزائرية عفوية ومحترمة (لا تستخدم فصحى معربة أو لهجات مشرقية إطلاقاً).
2. طابق نبرة ولهجة الزبون ({dialect['region']}) لتبني الثقة والقرب.
3. التزم بالحقائق المستخرجة أعلاه (خاصة الأسعار بالدينار والولايات) دون أي هلوسة.
4. اجعل الرد مختصراً وبشرياً (1 إلى 3 أسطر).
"""
    return prompt


def get_openai_tool_definitions() -> List[Dict[str, Any]]:
    """Return OpenAI / LLM function calling tools definitions for Algerian NLP."""
    return [
        {
            "type": "function",
            "function": {
                "name": "parse_algerian_message",
                "description": "Parse and extract Algerian entities (Wilayas, colloquial prices in DZD, payments, carriers, phones with telecom operator, quantities, product attributes) and dialect from customer text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The customer's message in Arabic, Arabizi, or French code-switching."
                        }
                    },
                    "required": ["text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_wilaya_details",
                "description": "Get official Algerian Wilaya information (Arabic/French name, postal code 01-69, region).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "integer",
                            "description": "The wilaya numeric code (1 to 69)."
                        }
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_human_escalation",
                "description": "Detect if customer is furious, making legal threats, or explicitly asking for a human agent.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The customer's message text."
                        }
                    },
                    "required": ["text"]
                }
            }
        }
    ]
