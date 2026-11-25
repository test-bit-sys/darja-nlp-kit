"""
AI Agent integration module for Algerian Darja communication.

Enables LLMs (GPT-4o, Gemini, Claude, Llama, Mistral) to understand and reply
in authentic Algerian Darja like a human merchant/representative.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from .normalizer import normalize
from .arabizi import arabizi_to_arabic
from .sentiment import analyze_sentiment
from .entities import extract_entities, get_wilaya_by_code
from .dialect import detect_dialect
from .intent import identify_intent, IntentType
from .escalation import detect_escalation
from .cultural import detect_cultural_references
from .dialogue import respond_to_darja
from .profanity import censor_profanity, detect_profanity
from .chat import DarjaChat

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
    cultural = detect_cultural_references(raw_message)

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
        "cultural": {
            "has_cultural_reference": cultural.has_cultural_reference,
            "summary": cultural.cultural_summary,
            "matches": [
                {
                    "matched_text": m.matched_text,
                    "category": m.category,
                    "canonical_name": m.canonical_name,
                    "meaning": m.meaning,
                }
                for m in cultural.all_matches
            ],
        },
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

    cult_data = context.get("cultural") or {}
    cultural_section = ""
    if cult_data.get("has_cultural_reference") or cult_data.get("hasCulturalReference"):
        cult_summary = cult_data.get("summary") or cult_data.get("culturalSummary") or ""
        cultural_section = f"\n[إشارات ثقافية وشعبية مرصودة في رسالة الزبون]:\n- الدلالات الشعبية: {cult_summary}\n👉 إرشاد الرد: أظهر فهماً ذكياً وتفاعلاً طيباً مع المثل الشعبي أو الأكلة أو المعلم المذكور بروح جزائرية أصيلة.\n"

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
{cultural_section}
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
        },
        {
            "type": "function",
            "function": {
                "name": "detect_cultural_references",
                "description": "Detect Algerian cultural references, proverbs, viral memes, landmarks, gastronomy, and slang in customer text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The customer's message text in Arabic or Arabizi."
                        }
                    },
                    "required": ["text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "respond_to_darja",
                "description": "Generate an authentic Algerian colloquial response (supporting 'wach ya khoy' -> 'we cv', greetings, and order inquiries).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The customer message to reply to."
                        },
                        "persona": {
                            "type": "string",
                            "enum": ["casual", "merchant", "assistant"],
                            "description": "Persona tone of the reply."
                        }
                    },
                    "required": ["text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "moderate_darja_text",
                "description": "Check text for Algerian profanity, vulgar expressions, slurs, and toxic language in Arabic script and Arabizi.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The message to check and sanitize."
                        }
                    },
                    "required": ["text"]
                }
            }
        }
    ]


LLM_PROVIDERS: Dict[str, Dict[str, str]] = {
    "openai": {"base_url": "https://api.openai.com/v1", "default_model": "gpt-4o-mini"},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "default_model": "gemini-2.5-flash"},
    "groq": {"base_url": "https://api.groq.com/openai/v1", "default_model": "llama-3.3-70b-versatile"},
    "deepseek": {"base_url": "https://api.deepseek.com/v1", "default_model": "deepseek-chat"},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1", "default_model": "meta-llama/llama-3.3-70b-instruct"},
    "ollama": {"base_url": "http://127.0.0.1:11434/v1", "default_model": "qwen2.5:7b"},
}


def execute_agent_tool(name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute any darja-nlp-kit AI Agent / MCP tool by name and return structured JSON dict."""
    args = arguments or {}

    if name == "parse_algerian_message":
        text = str(args.get("text", ""))
        ent = extract_entities(text)
        dia = detect_dialect(text)
        return {
            "dialect": {"region": dia.region, "confidence": dia.confidence, "markers": dia.detected_markers},
            "wilayas": [
                {"code": w.code, "name_ar": w.name_ar, "name_fr": w.name_fr, "commune": w.commune}
                for w in ent.wilayas
            ],
            "prices_dzd": [
                {"amount": p.amount, "raw": p.raw}
                for p in ent.prices if p.amount is not None
            ],
            "payments": [p.type for p in ent.payments],
            "deliveries": [d.company for d in (ent.deliveries or [])],
            "delivery_mode": ent.delivery_mode.mode if ent.delivery_mode else None,
            "phones": [
                {"normalized": ph.normalized, "operator": ph.operator, "whatsapp_url": ph.whatsapp_url}
                for ph in ent.phones
            ],
            "quantities": [{"value": q.value, "unit": q.unit, "raw": q.raw} for q in (ent.quantities or [])],
            "attributes": {
                "colors": ent.attributes.colors if ent.attributes else [],
                "sizes": ent.attributes.sizes if ent.attributes else [],
            },
        }

    if name == "get_wilaya_details":
        try:
            code = int(args.get("code", 0))
        except (TypeError, ValueError):
            code = 0
        w = get_wilaya_by_code(code)
        if w:
            return w
        return {"error": f"Wilaya code {code} not found (valid range: 1..69)"}

    if name == "check_human_escalation":
        text = str(args.get("text", ""))
        esc = detect_escalation(text)
        return {
            "needs_escalation": esc.needs_escalation,
            "reason": esc.reason,
            "urgency": esc.urgency,
            "matched_triggers": esc.matched_triggers,
            "guideline": esc.guideline,
        }

    if name == "detect_cultural_references":
        text = str(args.get("text", ""))
        cult = detect_cultural_references(text)
        return {
            "has_cultural_reference": cult.has_cultural_reference,
            "cultural_summary": cult.cultural_summary,
            "proverbs": [p.canonical_name for p in cult.proverbs],
            "memes_and_trends": [m.canonical_name for m in cult.memes_and_trends],
            "landmarks": [lm.canonical_name for lm in cult.landmarks],
            "gastronomy": [g.canonical_name for g in cult.gastronomy],
            "slang_expressions": [s.canonical_name for s in cult.slang_expressions],
        }

    if name == "respond_to_darja":
        text = str(args.get("text", ""))
        persona = str(args.get("persona", "casual"))
        res = respond_to_darja(text, persona=persona)  # type: ignore[arg-type]
        return {
            "reply": res.reply,
            "intent": res.intent,
            "script": res.script,
            "confidence": res.confidence,
            "source": res.source,
        }

    if name == "moderate_darja_text":
        text = str(args.get("text", ""))
        prof = detect_profanity(text)
        censored = censor_profanity(text)
        return {
            "is_profane": prof.is_profane,
            "severity": prof.severity,
            "matches": [{"term": m.term, "category": m.category, "severity": m.severity} for m in prof.matches],
            "censored_text": censored,
        }

    if name == "analyze_darja_message":
        from .pipeline import analyze
        text = str(args.get("text", ""))
        persona = str(args.get("persona", "merchant"))
        mode = str(args.get("sentiment_mode", "hybrid"))
        return analyze(text, persona=persona, sentiment_mode=mode).to_dict()  # type: ignore[arg-type]

    if name == "build_agent_prompt":
        text = str(args.get("text", ""))
        store = str(args.get("store_name", "Bazar El Djazair"))
        ctx = build_agent_context(text, store_name=store)
        return {"context": ctx, "system_prompt": format_agent_system_prompt(ctx)}

    return {"error": f"Unknown darja-nlp tool: {name}"}


def get_mcp_tool_definitions() -> List[Dict[str, Any]]:
    """Return MCP (Model Context Protocol) tool specifications covering all Algerian NLP tools."""
    mcp_tools = [
        {
            "name": item["function"]["name"],
            "description": item["function"]["description"],
            "inputSchema": item["function"]["parameters"],
        }
        for item in get_openai_tool_definitions()
    ]
    mcp_tools.extend([
        {
            "name": "analyze_darja_message",
            "description": "Run complete unified Algerian Darja analysis (sentiment, intent, dialect, entities, moderation, cultural references, and grounded reply).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Algerian Darja, Arabic, or Arabizi text."},
                    "persona": {"type": "string", "enum": ["casual", "merchant", "assistant"], "description": "Response persona."},
                    "sentiment_mode": {"type": "string", "enum": ["hybrid", "ml", "lexicon"], "description": "Sentiment engine mode."},
                },
                "required": ["text"],
            },
        },
        {
            "name": "build_agent_prompt",
            "description": "Extract structured grounded facts and generate an anti-hallucination Algerian Darja system prompt for an LLM.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Customer message."},
                    "store_name": {"type": "string", "description": "Optional store name."},
                },
                "required": ["text"],
            },
        },
    ])
    return mcp_tools


@dataclass
class AgentReply:
    """Structured response produced by DarjaAIAgent."""
    reply: str
    provider: str
    model: str
    intent: str
    dialect: str
    needs_escalation: bool
    slots: Dict[str, Any]
    ready_to_confirm: bool
    missing_slots: List[str]
    context: Dict[str, Any]
    tool_calls_executed: List[str] = field(default_factory=list)


class DarjaAIAgent:
    """Zero-dependency plug-and-play AI Agent for Algerian Darja (Offline + OpenAI/Gemini/Groq/DeepSeek/Ollama)."""

    def __init__(
        self,
        store_name: str = "Bazar El Djazair",
        persona: str = "merchant",
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.store_name = store_name
        self.persona = persona
        self.api_key = api_key or os.environ.get("DARJA_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if provider:
            self.provider = provider.lower()
        elif self.api_key or base_url:
            self.provider = "openai"
        else:
            self.provider = "offline"

        provider_cfg = LLM_PROVIDERS.get(self.provider, {})
        self.base_url = (base_url or provider_cfg.get("base_url", "")).rstrip("/")
        self.model = model or provider_cfg.get("default_model", "local-darja-rules")
        self.timeout = timeout
        self.chat_session = DarjaChat(store_name=store_name, persona=persona)  # type: ignore[arg-type]
        self.conversation_history: List[Dict[str, Any]] = []

    @property
    def slots(self) -> Dict[str, Any]:
        return self.chat_session.slots

    def reset(self) -> None:
        self.chat_session.reset()
        self.conversation_history.clear()

    def _call_openai_compatible(self, system_prompt: str, user_message: str) -> tuple[str, List[str]]:
        if self.provider != "ollama" and not self.api_key:
            raise ValueError(f"API key is required for provider '{self.provider}'. Set api_key or DARJA_API_KEY, or use provider='offline'.")

        messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history[-8:])
        messages.append({"role": "user", "content": user_message})
        tools = get_openai_tool_definitions()
        executed: List[str] = []

        for _ in range(3):
            payload = {
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
                "temperature": 0.4,
            }
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key or 'ollama'}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            msg = data["choices"][0]["message"]
            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                return str(msg.get("content") or "").strip(), executed

            messages.append(msg)
            for tc in tool_calls:
                fn = tc.get("function") or {}
                t_name = fn.get("name", "")
                try:
                    t_args = json.loads(fn.get("arguments") or "{}")
                except json.JSONDecodeError:
                    t_args = {}
                t_res = execute_agent_tool(t_name, t_args)
                executed.append(t_name)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", t_name),
                    "content": json.dumps(t_res, ensure_ascii=False),
                })

        return str(messages[-1].get("content") or ""), executed

    def ask(self, message: str) -> AgentReply:
        """Process a customer message, update slots, and generate a grounded Darja response."""
        turn = self.chat_session.send(message)
        ctx = build_agent_context(message, store_name=self.store_name)
        system_prompt = format_agent_system_prompt(ctx)

        reply_text = turn.reply
        used_provider = "offline"
        executed_tools: List[str] = []

        if self.provider != "offline" and not turn.escalation.needs_escalation:
            reply_text, executed_tools = self._call_openai_compatible(system_prompt, message)
            used_provider = self.provider

        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": reply_text})

        return AgentReply(
            reply=reply_text,
            provider=used_provider,
            model=self.model if used_provider != "offline" else "offline-darja-kb",
            intent=turn.intent,
            dialect=turn.dialect,
            needs_escalation=turn.escalation.needs_escalation,
            slots=turn.extracted_slots,
            ready_to_confirm=turn.ready_to_confirm,
            missing_slots=turn.missing_slots,
            context=ctx,
            tool_calls_executed=executed_tools,
        )

    @staticmethod
    def get_mcp_config(runtime: str = "python") -> Dict[str, Any]:
        """Generate plug-and-play MCP server configuration JSON for Claude Desktop, Cursor, VS Code, or Antigravity."""
        if runtime == "node":
            return {
                "mcpServers": {
                    "darja-nlp": {
                        "command": "npx",
                        "args": ["-y", "@dz-open-suite/darja-nlp-kit", "mcp"],
                    }
                }
            }
        return {
            "mcpServers": {
                "darja-nlp": {
                    "command": sys.executable,
                    "args": ["-m", "darja_nlp.cli", "mcp"],
                }
            }
        }

