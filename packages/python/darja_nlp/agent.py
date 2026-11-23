"""
AI Agent integration module for Algerian Darja communication.

Enables LLMs (GPT-4o, Gemini, Claude, Llama, Mistral) to understand and reply
in authentic Algerian Darja like a human merchant/representative.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from .normalizer import normalize
from .arabizi import arabizi_to_arabic
from .sentiment import analyze_sentiment
from .entities import extract_entities, get_wilaya_by_code
from .dialect import detect_dialect


def build_agent_context(message: str, store_name: str = "Bazar El Djazair") -> Dict[str, Any]:
    """
    Process a raw Algerian message and build a structured, ground-truth context
    for AI agents and LLMs.
    """
    raw_message = message or ""
    arabic_trans = arabizi_to_arabic(raw_message)
    normalized = normalize(raw_message)

    # Dialect, sentiment, and entity extraction
    dialect = detect_dialect(raw_message)
    sentiment = analyze_sentiment(raw_message)
    entities = extract_entities(raw_message)

    # Dialect instructions mapping
    dialect_guidelines = {
        "WEST": "لهجة الغرب الجزائري (وهران وتلمسان): استعمل كلمات خفيفة مثل (درك، غايا، مرحبا بيك خويا، ما تقلقش روحك).",
        "EAST": "لهجة الشرق الجزائري (قسنطينة وسطيف وعنابة): استعمل كلمات دافئة مثل (عيشك، ضرك، وشبيك، على عيني، ما كاش مشكل).",
        "CENTER": "لهجة الوسط والعاصمة (الجزائر والبليدة): استعمل أسلوب العاصمة السلس (واش خويا، مرحبا بيك، رانا هنا، كاش ما تسحق).",
        "SOUTH": "لهجة الجنوب الجزائري الكريمة: استعمل كلمات الترحيب والأصالة (مرحبا بيك، ربي يحفظك، على راسنا وعينينا).",
        "GENERAL_DARJA": "دارجة جزائرية عامة ومفهومة ومحترمة تجمع بين العفوية واللباقة المهنية."
    }

    # Tone recommendation based on sentiment
    if sentiment.label == "NEGATIVE":
        tone = "APOLOGETIC_AND_REASSURING"
        tone_instruction = "⚠️ الزبون غاضب أو يشتكي! ابدأ بتطييب الخاطر والاعتذار ('حقك علينا خويا، ما تقلقش، المشكل نحلوه درك'). تجنب الجفاف والردود الآلية."
    elif sentiment.label == "POSITIVE":
        tone = "WARM_AND_CELEBRATING"
        tone_instruction = "😊 الزبون مسرور وراضٍ. رد بابتماس وترحاب حار ('ربي يحفظك، شهادة نعتزوا بيها، سلعة لوز لزبائننا')."
    else:
        tone = "PROFESSIONAL_HELPFUL"
        tone_instruction = "🤝 الزبون يستفسر. أجب بوضوح وسرعة ومهنية جزائرية عفوية."

    wilayas_summary = [f"{w.name_ar} ({w.code_str})" for w in entities.wilayas]
    payments_summary = [p.label for p in entities.payments]
    prices_summary = [f"{p.amount:,.0f} دج ({p.raw})" for p in entities.prices if p.amount is not None]
    deliveries_summary = [d.label for d in entities.deliveries]
    delivery_mode_summary = entities.delivery_mode.label if entities.delivery_mode else None
    phones_summary = [ph.normalized for ph in entities.phones]

    return {
        "store_name": store_name,
        "raw_message": raw_message,
        "arabic_transliterated": arabic_trans,
        "normalized": normalized,
        "dialect": {
            "region": dialect.region,
            "confidence": dialect.confidence,
            "detected_markers": dialect.detected_markers,
            "guideline": dialect_guidelines.get(dialect.region, dialect_guidelines["GENERAL_DARJA"]),
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
        },
    }


def format_agent_system_prompt(context: Dict[str, Any]) -> str:
    """Format a system prompt for an LLM based on extracted agent context."""
    store = context.get("store_name", "المتجر")
    dialect = context["dialect"]
    sentiment = context["sentiment"]
    facts = context["grounded_facts"]

    prompt = f"""أنت مساعد خدمة عملاء ذكي وبشري جداً لمتجر إلكتروني جزائري '{store}'.
مهمتك الرد على الزبون الجزائري بدارجة واقعية ومتقنة 100%، كأنك تاجر جزائري محترف ولطيف.

[السياق المستخرج من رسالة الزبون]:
- الرسالة: "{context['raw_message']}"
- الترجمة التفسيرية (إذا كانت عربيزي): "{context['arabic_transliterated']}"
- المنطقة الجغرافية للهجة: {dialect['region']} ({dialect['guideline']})
- حالة الزبون النفسية: {sentiment['label']} (الدرجة: {sentiment['score']})
- إرشادات النبرة: {sentiment['tone_instruction']}
- الولايات المؤكدة: {', '.join(facts['wilayas']) if facts['wilayas'] else 'غير محددة'}
- المبالغ المذكورة بالدينار: {', '.join(facts['prices_dzd']) if facts['prices_dzd'] else 'غير محددة'}
- وسائل الدفع المرصودة: {', '.join(facts['payments']) if facts['payments'] else 'غير محددة'}
- شركات التوصيل: {', '.join(facts['delivery_companies']) if facts['delivery_companies'] else 'غير محددة'}
- نمط التوصيل: {facts['delivery_mode'] if facts['delivery_mode'] else 'غير محدد'}
- أرقام الهاتف: {', '.join(facts['phones']) if facts['phones'] else 'غير متوفرة'}

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
                "description": "Parse and extract Algerian entities (Wilayas, colloquial prices in DZD, payments, carriers, phones) and dialect from customer text.",
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
        }
    ]
