"""Algerian Darja conversational dialogue response engine (Natural Algerian Chat)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from .intent import identify_intent, IntentType
from .sentiment import analyze_sentiment

_DATA_DIR = Path(__file__).resolve().parent / "data"

PersonaType = Literal["casual", "merchant", "assistant"]
ScriptType = Literal["auto", "arabizi", "arabic"]

@dataclass
class DialogueResponse:
    reply: str
    intent: str
    script: Literal["arabizi", "arabic"]
    confidence: float
    matched_pattern: Optional[str] = None

_dialogue_rules: Optional[Dict[str, Any]] = None

def load_dialogue_rules() -> Dict[str, Any]:
    global _dialogue_rules
    if _dialogue_rules is not None:
        return _dialogue_rules

    path = _DATA_DIR / "dialogue_rules.json"
    with open(path, "r", encoding="utf-8") as f:
        _dialogue_rules = json.load(f)
    return _dialogue_rules

def _detect_script(text: str) -> Literal["arabizi", "arabic"]:
    """Detect if message is predominantly Arabizi or Arabic script."""
    latin_count = len(re.findall(r'[a-zA-Z]', text))
    arabic_count = len(re.findall(r'[\u0600-\u06FF]', text))
    return "arabic" if arabic_count > latin_count else "arabizi"

def _normalize_chat_input(text: str) -> str:
    """Normalize repeated characters, punctuation, and casing."""
    t = text.lower().strip()
    # Remove excessive punctuation
    t = re.sub(r'[!?.,;:\-_/\\]+', ' ', t)
    # Normalize tashkeel and tatweel
    t = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', t)
    # Collapse repetitive letters (3+ down to 1 or 2)
    t = re.sub(r'(.)\1{2,}', r'\1', t)
    # Collapse whitespace
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def respond_to_darja(
    text: str,
    persona: PersonaType = "casual",
    script: ScriptType = "auto"
) -> DialogueResponse:
    """Generate an authentic, natural Algerian Darja conversational response."""
    if not text or not text.strip():
        return DialogueResponse(
            reply="We cv kho, kash ma khasek?" if script == "arabizi" else "مرحباً بيك خويا، كاش ما نسحقو نخدموك؟",
            intent="EMPTY",
            script="arabizi" if script == "arabizi" else "arabic",
            confidence=1.0
        )

    resolved_script = _detect_script(text) if script == "auto" else script
    norm_input = _normalize_chat_input(text)
    rules_data = load_dialogue_rules()
    rules = rules_data.get("rules", [])

    # 1. Exact or Substring Matching in dialogue rules
    for rule in rules:
        intent = rule.get("intent", "CASUAL_CHAT")
        patterns = rule.get("patterns_arabizi" if resolved_script == "arabizi" else "patterns_arabic", [])
        
        # Also check cross-script patterns if user passed arabic in auto mode or vice versa
        alt_patterns = rule.get("patterns_arabic" if resolved_script == "arabizi" else "patterns_arabizi", [])

        for p in patterns:
            norm_p = _normalize_chat_input(p)
            if norm_p in norm_input or norm_input in norm_p:
                responses = rule.get("responses_arabizi" if resolved_script == "arabizi" else "responses_arabic", [])
                chosen_reply = responses[0] if responses else ""
                
                # Persona customization
                if persona == "merchant" and intent == "WELLBEING_INQUIRY":
                    if resolved_script == "arabizi":
                        chosen_reply = "We cv hamdoulah kho! Marhba bik f la boutique ta3na, kash ma khasek sel3a?"
                    else:
                        chosen_reply = "لاباس الحمد لله ربي يحفظك خويا! مرحباً بيك في متجرنا، كاش ما راك تحوس سلعة؟"
                elif persona == "assistant" and intent == "WELLBEING_INQUIRY":
                    if resolved_script == "arabizi":
                        chosen_reply = "Hamdoullah kolchi bkhir! Kifech n9der n3awnek lyoum kho?"
                    else:
                        chosen_reply = "الحمد لله على خير خويا! كيفاش نقدر نعاونك اليوم في استفسارك؟"

                return DialogueResponse(
                    reply=chosen_reply,
                    intent=intent,
                    script=resolved_script,
                    confidence=0.95,
                    matched_pattern=p
                )

        # Cross-pattern check
        for p in alt_patterns:
            norm_p = _normalize_chat_input(p)
            if norm_p in norm_input:
                responses = rule.get("responses_arabizi" if resolved_script == "arabizi" else "responses_arabic", [])
                chosen_reply = responses[0] if responses else ""
                return DialogueResponse(
                    reply=chosen_reply,
                    intent=intent,
                    script=resolved_script,
                    confidence=0.90,
                    matched_pattern=p
                )

    # 2. Fallback using intent classifier
    intent_res = identify_intent(text)
    detected_intent = intent_res.primary_intent

    if detected_intent == "GREETING":
        if resolved_script == "arabizi":
            reply = "We cv hamdoulah w nta kho? Marhba bik!"
        else:
            reply = "مرحباً بيك خويا العزيز! واش راك وكاش ما نسحقو نخدموك؟"
        return DialogueResponse(reply=reply, intent="GREETING", script=resolved_script, confidence=0.85)

    if detected_intent == Intent.PRICE_INQUIRY:
        if resolved_script == "arabizi":
            reply = "Marhba bik kho! Souma mrigla w kayna livraison rapide l ga3 69 wilaya."
        else:
            reply = "مرحباً بيك خويا! السومة مريڤلة بزاف والتوصيل متوفر لجميع 69 ولاية."
        return DialogueResponse(reply=reply, intent="PRICE_INQUIRY", script=resolved_script, confidence=0.85)

    if detected_intent == Intent.COMPLAINT:
        if resolved_script == "arabizi":
            reply = "Hassinek kho w smahlna 3la had l'erreur! Ab3atli numéro ta3 la commande w nreglouhalek f lwa9t."
        else:
            reply = "حقك علينا خويا ونعتذرو منك! ابعثلي رقم الطلبية ونريڤلوهالك فوراً بإذن الله."
        return DialogueResponse(reply=reply, intent="COMPLAINT", script=resolved_script, confidence=0.85)

    # General default fallback
    if resolved_script == "arabizi":
        reply = "We cv kho! Marhba bik, kifech n9edrou n3awnouk lyoum?"
    else:
        reply = "مرحباً بيك خويا الغالي! كيفاش نقدرو نعاونوك اليوم في خدمتك؟"

    return DialogueResponse(
        reply=reply,
        intent="CASUAL_CHAT",
        script=resolved_script,
        confidence=0.75
    )
