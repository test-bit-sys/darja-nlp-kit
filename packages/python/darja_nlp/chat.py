"""Stateful multi-turn conversational session manager for Algerian Darja e-commerce & AI bots."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

from .dialect import DialectRegion, detect_dialect
from .dialogue import PersonaType, ScriptType, respond_to_darja
from .entities import extract_entities
from .escalation import EscalationResult, detect_escalation
from .intent import identify_intent


@dataclass
class ChatMessage:
    role: Literal["user", "assistant"]
    text: str
    intent: str


@dataclass
class ChatTurnResult:
    reply: str
    intent: str
    script: Literal["arabizi", "arabic"]
    dialect: DialectRegion
    extracted_slots: Dict[str, Any]
    missing_slots: List[str]
    ready_to_confirm: bool
    escalation: EscalationResult
    history: List[ChatMessage] = field(default_factory=list)


class DarjaChat:
    """Multi-turn stateful Algerian Darja conversation handler.

    Automatically remembers extracted wilayas, communes, phone numbers,
    quantities, product colors/sizes, delivery company/mode, payments, prices,
    regional dialect, and preferred script across turns.
    """

    def __init__(
        self,
        store_name: str = "Bazar El Djazair",
        persona: PersonaType = "merchant",
        script: ScriptType = "auto",
        custom_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.store_name = store_name
        self.persona = persona
        self.script = script
        self.custom_rules = list(custom_rules or [])
        self.reset()

    def reset(self) -> None:
        """Clear conversation history and accumulated order/customer slots."""
        self.history: List[ChatMessage] = []
        self.detected_dialect: DialectRegion = "GENERAL_DARJA"
        self.preferred_script: Optional[Literal["arabizi", "arabic"]] = None
        self.active_intent: str = "UNKNOWN"
        self.slots: Dict[str, Any] = {
            "wilayas": [],
            "phones": [],
            "deliveries": [],
            "delivery_mode": None,
            "payments": [],
            "prices_dzd": [],
            "quantities": [],
            "colors": [],
            "sizes": [],
        }

    def _detect_script(self, text: str) -> Literal["arabizi", "arabic"]:
        latin_count = len(re.findall(r"[a-zA-Z]", text))
        arabic_count = len(re.findall(r"[\u0600-\u06FF]", text))
        if arabic_count == 0 and latin_count == 0 and self.preferred_script:
            return self.preferred_script
        return "arabic" if arabic_count > latin_count else "arabizi"

    def _merge_entities(self, text: str) -> List[str]:
        """Extract entities from current turn and merge newly supplied slots."""
        ent = extract_entities(text)
        newly_captured: List[str] = []

        existing_w = {w["code"] for w in self.slots["wilayas"]}
        for w in ent.wilayas:
            if w.code not in existing_w:
                self.slots["wilayas"].append({
                    "code": w.code,
                    "name_ar": w.name_ar,
                    "name_fr": w.name_fr,
                    "commune": w.commune,
                })
                existing_w.add(w.code)
                if "wilaya" not in newly_captured:
                    newly_captured.append("wilaya")

        existing_p = {p["normalized"] for p in self.slots["phones"]}
        for p in ent.phones:
            if p.normalized not in existing_p:
                self.slots["phones"].append({
                    "normalized": p.normalized,
                    "operator": p.operator_label,
                    "whatsapp": p.whatsapp_url,
                })
                existing_p.add(p.normalized)
                if "phone" not in newly_captured:
                    newly_captured.append("phone")

        for d in ent.deliveries:
            if d.label not in self.slots["deliveries"]:
                self.slots["deliveries"].append(d.label)

        if ent.delivery_mode and not self.slots["delivery_mode"]:
            self.slots["delivery_mode"] = ent.delivery_mode.label

        for pay in ent.payments:
            if pay.label not in self.slots["payments"]:
                self.slots["payments"].append(pay.label)

        for pr in ent.prices:
            if pr.amount is not None and pr.amount not in self.slots["prices_dzd"]:
                self.slots["prices_dzd"].append(pr.amount)

        for q in (ent.quantities or []):
            q_obj = {"value": q.value, "unit": q.unit, "raw": q.raw}
            if q_obj not in self.slots["quantities"]:
                self.slots["quantities"].append(q_obj)
                if "quantity" not in newly_captured:
                    newly_captured.append("quantity")

        if ent.attributes:
            for c in ent.attributes.colors:
                if c not in self.slots["colors"]:
                    self.slots["colors"].append(c)
            for s in ent.attributes.sizes:
                if s not in self.slots["sizes"]:
                    self.slots["sizes"].append(s)

        return newly_captured

    def send(self, message: str, vary: bool = False) -> ChatTurnResult:
        """Process one user turn while preserving context and accumulated slots."""
        msg = (message or "").strip()
        turn_script: Literal["arabizi", "arabic"] = (
            self._detect_script(msg) if self.script == "auto" else self.script  # type: ignore[assignment]
        )
        if msg:
            self.preferred_script = turn_script

        esc = detect_escalation(msg)
        dia = detect_dialect(msg)
        if dia.region != "GENERAL_DARJA":
            self.detected_dialect = dia.region

        intent_res = identify_intent(msg)
        if intent_res.intent != "UNKNOWN":
            self.active_intent = intent_res.intent

        newly_captured = self._merge_entities(msg)
        self.history.append(ChatMessage(role="user", text=msg, intent=intent_res.intent))

        missing_slots: List[str] = []
        if not self.slots["wilayas"]:
            missing_slots.append("wilaya")
        if not self.slots["phones"]:
            missing_slots.append("phone")
        ready_to_confirm = len(missing_slots) == 0

        is_order_flow = self.active_intent in ("ORDER", "DELIVERY_INQUIRY") or bool(newly_captured)

        if esc.needs_escalation:
            reply_text = (
                "Smahlna bzaf kho! Rani n7awel had l'message drk l'responsable bach yreglihleek koulchi."
                if turn_script == "arabizi"
                else "نعتذرو منك بزاف خويا! راني نحول رسالتك فوراً للمسؤول باش يتواصل معاك ويريڤليلك الإشكال."
            )
            turn_intent = f"ESCALATION_{esc.reason or 'ALERT'}"
        elif is_order_flow and ready_to_confirm and newly_captured:
            w = self.slots["wilayas"][-1]
            ph = self.slots["phones"][-1]["normalized"]
            w_label = f"{w['name_fr']} ({w['code']})" if turn_script == "arabizi" else f"{w['name_ar']} ({w['code']})"
            reply_text = (
                f"Sahit kho! La commande ta3ek mrigla w confirmée: wilaya {w_label}, téléphone {ph}. Livraison f 24-48h!"
                if turn_script == "arabizi"
                else f"صحيت خويا! طلبيتك مؤكدة ومسجلة: ولاية {w_label}، الهاتف {ph}. التوصيل يوصلك خلال 24-48 ساعة!"
            )
            turn_intent = "ORDER_CONFIRMED"
        elif self.active_intent == "ORDER" and not ready_to_confirm and (
            newly_captured or intent_res.intent == "ORDER"
        ):
            if "wilaya" in missing_slots and "phone" in missing_slots:
                reply_text = (
                    "Marhba bik kho! Ab3atli bark lwilaya w numéro de téléphone bach nconfirmiwlek la commande."
                    if turn_script == "arabizi"
                    else "مرحباً بيك خويا! ابعثلي برك الولاية ورقم الهاتف باش نسجلو ونكونفيرميولك الطلبية."
                )
            elif "phone" in missing_slots:
                w = self.slots["wilayas"][-1]
                w_label = w["name_fr"] if turn_script == "arabizi" else w["name_ar"]
                reply_text = (
                    f"C'est bon lwilaya {w_label} msajla! Ba9i ghi numéro de téléphone kho bach nvalidiw la commande."
                    if turn_script == "arabizi"
                    else f"ممتاز، ولاية {w_label} مسجلة! بقالنا برك رقم الهاتف خويا باش نكونفيرميولك الطلبية."
                )
            else:
                ph = self.slots["phones"][-1]["normalized"]
                reply_text = (
                    f"Numéro {ph} msajel kho! 9olli bark chmen wilaya w nwalou f lwa9t."
                    if turn_script == "arabizi"
                    else f"رقم الهاتف {ph} مسجل خويا! قولي برك واش من ولاية باش نكملو الطلب."
                )
            turn_intent = "ORDER_SLOT_FILLING"
        else:
            d_res = respond_to_darja(
                msg,
                persona=self.persona,
                script=turn_script,
                vary=vary,
                custom_rules=self.custom_rules or None,
            )
            reply_text = d_res.reply
            turn_intent = d_res.intent

        self.history.append(ChatMessage(role="assistant", text=reply_text, intent=turn_intent))

        return ChatTurnResult(
            reply=reply_text,
            intent=turn_intent,
            script=turn_script,
            dialect=self.detected_dialect,
            extracted_slots={k: (list(v) if isinstance(v, list) else v) for k, v in self.slots.items()},
            missing_slots=missing_slots,
            ready_to_confirm=ready_to_confirm,
            escalation=esc,
            history=list(self.history),
        )
