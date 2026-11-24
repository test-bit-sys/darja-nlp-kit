"""Algerian Darja conversational dialogue response engine (Rules + Real KB Retrieval)."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Tuple

from .intent import identify_intent

_DATA_DIR = Path(__file__).resolve().parent / "data"

PersonaType = Literal["casual", "merchant", "assistant"]
ScriptType = Literal["auto", "arabizi", "arabic"]
DialogueStrategy = Literal["auto", "rules", "retrieval"]

_KB_STOP = frozenset({
    "el", "al", "la", "le", "les", "de", "du", "un", "une", "et", "ou", "en",
    "wa", "w", "f", "fi", "fel", "l", "li", "ta3", "taa", "men", "mn", "min",
    "b", "bi", "ala", "3la", "ya", "في", "من", "على", "الى", "إلى", "عن", "مع",
    "و", "أو", "او", "ال", "لي", "تاع", "نتاع", "ديال", "وش", "واش", "يا", "راها", "راهو",
})


@dataclass
class DialogueResponse:
    reply: str
    intent: str
    script: Literal["arabizi", "arabic"]
    confidence: float
    matched_pattern: Optional[str] = None
    source: str = "rule"


_dialogue_rules: Optional[Dict[str, Any]] = None
_kb_cache: Optional[Dict[str, Any]] = None
_kb_index: Optional[Tuple[Dict[str, List[int]], List[Dict[str, float]], Dict[str, float]]] = None


def load_dialogue_rules() -> Dict[str, Any]:
    global _dialogue_rules
    if _dialogue_rules is not None:
        return _dialogue_rules

    path = _DATA_DIR / "dialogue_rules.json"
    with open(path, "r", encoding="utf-8") as f:
        _dialogue_rules = json.load(f)
    return _dialogue_rules


def _kb_tokenize(text: str) -> List[str]:
    t = _normalize_chat_input(text)
    toks = re.findall(r"[a-z0-9\u0600-\u06FF']+", t)
    return [tok for tok in toks if len(tok) >= 2 and tok not in _KB_STOP]


def load_dialogue_kb() -> List[Dict[str, Any]]:
    global _kb_cache, _kb_index
    if _kb_cache is None:
        kb_path = _DATA_DIR / "dialogue_kb.json"
        if kb_path.exists():
            try:
                with open(kb_path, "r", encoding="utf-8") as f:
                    _kb_cache = json.load(f)
            except Exception:
                _kb_cache = {"entries": []}
        else:
            _kb_cache = {"entries": []}

    entries: List[Dict[str, Any]] = _kb_cache.get("entries", [])
    if _kb_index is None and entries:
        inv: Dict[str, List[int]] = {}
        df: Dict[str, int] = {}
        doc_toks: List[List[str]] = []
        for idx, entry in enumerate(entries):
            toks = list(set(_kb_tokenize(entry.get("prompt", ""))))
            doc_toks.append(toks)
            for tok in toks:
                df[tok] = df.get(tok, 0) + 1
                inv.setdefault(tok, []).append(idx)

        n_docs = len(entries)
        idf: Dict[str, float] = {
            tok: math.log((n_docs + 1.0) / (freq + 1.0)) + 1.0
            for tok, freq in df.items()
        }
        doc_vecs: List[Dict[str, float]] = []
        for toks in doc_toks:
            vec = {tok: idf[tok] for tok in toks}
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            doc_vecs.append({k: v / norm for k, v in vec.items()})
        _kb_index = (inv, doc_vecs, idf)

    return entries


def _detect_script(text: str) -> Literal["arabizi", "arabic"]:
    """Detect if message is predominantly Arabizi or Arabic script."""
    latin_count = len(re.findall(r'[a-zA-Z]', text))
    arabic_count = len(re.findall(r'[\u0600-\u06FF]', text))
    return "arabic" if arabic_count > latin_count else "arabizi"


def _normalize_chat_input(text: str) -> str:
    """Normalize repeated characters, punctuation, and casing."""
    t = text.lower().strip()
    t = re.sub(r'[!?.,;:\-_/\\]+', ' ', t)
    t = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', t)
    t = re.sub(r'[أإآ]', 'ا', t).replace('ة', 'ه').replace('ى', 'ي')
    t = re.sub(r'(.)\1{2,}', r'\1', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def _pick_response(responses: List[str], norm_input: str, vary: bool) -> str:
    if not responses:
        return ""
    if not vary or len(responses) == 1:
        return responses[0]
    idx = sum(ord(ch) for ch in norm_input) % len(responses)
    return responses[idx]


def _search_kb(text: str, preferred_script: Literal["arabizi", "arabic"]) -> Optional[Tuple[Dict[str, Any], float]]:
    entries = load_dialogue_kb()
    if not entries or _kb_index is None:
        return None
    inv, doc_vecs, idf = _kb_index
    q_toks = _kb_tokenize(text)
    if len(q_toks) < 2:
        return None

    q_vec: Dict[str, float] = {}
    for tok in set(q_toks):
        q_vec[tok] = idf.get(tok, 1.0)
    q_norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1.0
    q_vec = {k: v / q_norm for k, v in q_vec.items()}

    candidates: set[int] = set()
    for tok in q_vec:
        if tok in inv:
            candidates.update(inv[tok])

    if not candidates:
        return None

    best_entry: Optional[Dict[str, Any]] = None
    best_score = 0.0

    for idx in candidates:
        d_vec = doc_vecs[idx]
        sim = sum(q_vec[t] * d_vec.get(t, 0.0) for t in q_vec)
        entry = entries[idx]
        if entry.get("script") == preferred_script:
            sim += 0.06
        if sim > best_score:
            best_score = sim
            best_entry = entry

    if best_entry is not None and best_score >= 0.34:
        return best_entry, best_score
    return None


def respond_to_darja(
    text: str,
    persona: PersonaType = "casual",
    script: ScriptType = "auto",
    strategy: DialogueStrategy = "auto",
    vary: bool = False,
    custom_rules: Optional[List[Dict[str, Any]]] = None,
) -> DialogueResponse:
    """Generate an authentic Algerian Darja response via rule matching + real conversational KB retrieval."""
    if not text or not text.strip():
        default_script: Literal["arabizi", "arabic"] = "arabizi" if script == "arabizi" else "arabic"
        return DialogueResponse(
            reply="We cv kho, kash ma khasek?" if default_script == "arabizi" else "مرحباً بيك خويا، كاش ما نسحقو نخدموك؟",
            intent="EMPTY",
            script=default_script,
            confidence=1.0,
            source="default",
        )

    resolved_script: Literal["arabizi", "arabic"] = _detect_script(text) if script == "auto" else script  # type: ignore[assignment]
    norm_input = _normalize_chat_input(text)

    if strategy != "retrieval":
        rules_data = load_dialogue_rules()
        base_rules = rules_data.get("rules", [])
        all_rules: List[Tuple[bool, Dict[str, Any]]] = []
        if custom_rules:
            for cr in custom_rules:
                all_rules.append((True, cr))
        for br in base_rules:
            all_rules.append((False, br))

        best_match: Optional[Tuple[int, str, bool, Dict[str, Any], float]] = None

        for is_custom, rule in all_rules:
            patterns = rule.get("patterns_arabizi" if resolved_script == "arabizi" else "patterns_arabic", [])
            alt_patterns = rule.get("patterns_arabic" if resolved_script == "arabizi" else "patterns_arabizi", [])

            for p in patterns:
                norm_p = _normalize_chat_input(p)
                if not norm_p:
                    continue
                score = 0
                if norm_input == norm_p:
                    score = len(norm_p) + 200
                elif norm_p in norm_input:
                    score = len(norm_p) + 25
                elif len(norm_input) >= 4 and norm_input in norm_p:
                    score = len(norm_input) + 5
                if score > 0:
                    if is_custom:
                        score += 50
                    if best_match is None or score > best_match[0]:
                        best_match = (score, p, is_custom, rule, 0.95)

            for p in alt_patterns:
                norm_p = _normalize_chat_input(p)
                if not norm_p:
                    continue
                if norm_p in norm_input:
                    score = len(norm_p) + (40 if is_custom else 10)
                    if best_match is None or score > best_match[0]:
                        best_match = (score, p, is_custom, rule, 0.90)

        if best_match is not None:
            _, matched_p, is_custom, rule, conf = best_match
            intent = rule.get("intent", "CASUAL_CHAT")
            responses = rule.get("responses_arabizi" if resolved_script == "arabizi" else "responses_arabic", [])
            chosen_reply = _pick_response(responses, norm_input, vary)

            if not is_custom and intent == "WELLBEING_INQUIRY":
                if persona == "merchant":
                    chosen_reply = (
                        "We cv hamdoulah kho! Marhba bik f la boutique ta3na, kash ma khasek sel3a?"
                        if resolved_script == "arabizi"
                        else "لاباس الحمد لله ربي يحفظك خويا! مرحباً بيك في متجرنا، كاش ما راك تحوس سلعة؟"
                    )
                elif persona == "assistant":
                    chosen_reply = (
                        "Hamdoullah kolchi bkhir! Kifech n9der n3awnek lyoum kho?"
                        if resolved_script == "arabizi"
                        else "الحمد لله على خير خويا! كيفاش نقدر نعاونك اليوم في استفسارك؟"
                    )

            return DialogueResponse(
                reply=chosen_reply,
                intent=intent,
                script=resolved_script,
                confidence=conf,
                matched_pattern=matched_p,
                source="custom_rule" if is_custom else "rule",
            )

    # Retrieval over real curated KB (DziriAlign + DziriEval)
    if strategy in ("auto", "retrieval"):
        kb_hit = _search_kb(text, resolved_script)
        if kb_hit is not None:
            entry, sim = kb_hit
            entry_script: Literal["arabizi", "arabic"] = (
                resolved_script if script != "auto" else entry.get("script", resolved_script)
            )
            return DialogueResponse(
                reply=entry["reply"],
                intent=entry.get("intent", "CONVERSATION"),
                script=entry_script,
                confidence=round(min(0.92, 0.55 + sim * 0.5), 2),
                matched_pattern=entry.get("prompt"),
                source="kb_retrieval",
            )

    # Fallback using intent classifier
    intent_res = identify_intent(text)
    detected_intent = intent_res.intent

    if detected_intent == "GREETING":
        reply = (
            "We cv hamdoulah w nta kho? Marhba bik!"
            if resolved_script == "arabizi"
            else "مرحباً بيك خويا العزيز! واش راك وكاش ما نسحقو نخدموك؟"
        )
        return DialogueResponse(reply=reply, intent="GREETING", script=resolved_script, confidence=0.85, source="intent_fallback")

    if detected_intent == "PRICE_INQUIRY":
        reply = (
            "Marhba bik kho! Souma mrigla w kayna livraison rapide l ga3 69 wilaya."
            if resolved_script == "arabizi"
            else "مرحباً بيك خويا! السومة مريڤلة بزاف والتوصيل متوفر لجميع 69 ولاية."
        )
        return DialogueResponse(reply=reply, intent="PRICE_INQUIRY", script=resolved_script, confidence=0.85, source="intent_fallback")

    if detected_intent == "ORDER":
        reply = (
            "Marhba bik kho! Ab3atli lwilaya, l'adresse w numéro de téléphone w nconfirmiwlek la commande."
            if resolved_script == "arabizi"
            else "مرحباً بيك خويا! ابعثلي الولاية، العنوان ورقم الهاتف باش نسجلو طلبيتك فوراً."
        )
        return DialogueResponse(reply=reply, intent="ORDER", script=resolved_script, confidence=0.85, source="intent_fallback")

    if detected_intent == "DELIVERY_INQUIRY":
        reply = (
            "Kayna livraison rapide l ga3 69 wilaya (24-48h) l bab dar wla stop desk!"
            if resolved_script == "arabizi"
            else "التوصيل متوفر لجميع 69 ولاية في ظرف 24 إلى 48 ساعة لباب الدار أو المكتب!"
        )
        return DialogueResponse(reply=reply, intent="DELIVERY_INQUIRY", script=resolved_script, confidence=0.85, source="intent_fallback")

    if detected_intent == "AVAILABILITY_INQUIRY":
        reply = (
            "Ih kho mazalha dispo f stock! Marhba bik idha rak hab tcommandi."
            if resolved_script == "arabizi"
            else "إيه خويا مازالها متوفرة في الستوك! مرحباً بيك إذا راك حاب تطلبها."
        )
        return DialogueResponse(reply=reply, intent="AVAILABILITY_INQUIRY", script=resolved_script, confidence=0.85, source="intent_fallback")

    if detected_intent == "COMPLAINT":
        reply = (
            "Hassinek kho w smahlna 3la had l'erreur! Ab3atli numéro ta3 la commande w nreglouhalek f lwa9t."
            if resolved_script == "arabizi"
            else "حقك علينا خويا ونعتذرو منك! ابعثلي رقم الطلبية ونريڤلوهالك فوراً بإذن الله."
        )
        return DialogueResponse(reply=reply, intent="COMPLAINT", script=resolved_script, confidence=0.85, source="intent_fallback")

    reply = (
        "We cv kho! Marhba bik, kifech n9edrou n3awnouk lyoum?"
        if resolved_script == "arabizi"
        else "مرحباً بيك خويا الغالي! كيفاش نقدرو نعاونوك اليوم في خدمتك؟"
    )
    return DialogueResponse(
        reply=reply,
        intent="CASUAL_CHAT",
        script=resolved_script,
        confidence=0.75,
        source="default",
    )
