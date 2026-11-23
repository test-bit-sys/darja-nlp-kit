"""
Algerian E-Commerce WhatsApp Automation Webhook Bot.
Zero external dependencies (uses standard library http.server).

Features:
- Handles WhatsApp Cloud API / Twilio webhooks.
- Extracts Algerian Wilaya (1-69), Communes, Phone, and Telecom Operator.
- Extracts colloquial quantities ('زوج حبات', 'شكارة', 'دوزينة') and product sizes/colors.
- Real-time Human Escalation Detection (angry customer, dispute, chargeback threat).
- Generates tailored, 100% human-like Darja reply prompts for GPT-4o / Gemini.
"""

from __future__ import annotations

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict

# Ensure local darja_nlp package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages", "python")))

from darja_nlp import (
    build_agent_context,
    detect_escalation,
    extract_entities,
    format_agent_system_prompt,
    identify_intent,
)


class WhatsAppWebhookHandler(BaseHTTPRequestHandler):
    """Webhook server for WhatsApp & Algerian E-Commerce Customer Chat."""

    def do_GET(self):
        """WhatsApp webhook verification challenge (hub.challenge)."""
        if "hub.challenge" in self.path:
            from urllib.parse import parse_qs, urlparse
            query = parse_qs(urlparse(self.path).query)
            challenge = query.get("hub.challenge", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(challenge.encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "running", "bot": "Algerian Darja E-Commerce AI"}).encode("utf-8"))

    def do_POST(self):
        """Process incoming customer message from WhatsApp."""
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(post_data)
        except Exception:
            payload = {"message": post_data}

        # Extract text from standard WhatsApp Cloud payload or simple payload
        incoming_text = ""
        sender_phone = ""
        try:
            entry = payload.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [{}])
            incoming_text = messages[0].get("text", {}).get("body", "")
            sender_phone = messages[0].get("from", "")
        except Exception:
            incoming_text = payload.get("text") or payload.get("message") or ""
            sender_phone = payload.get("from") or payload.get("phone") or ""

        if not incoming_text:
            self.send_response(200)
            self.end_headers()
            return

        print(f"\n📩 New Customer Message from {sender_phone}:")
        print(f"   \"{incoming_text}\"")

        # 1. Step 1: Check for urgent escalation
        escalation = detect_escalation(incoming_text)
        if escalation.needs_escalation:
            print(f"🚨 [CRITICAL ALERT] Escalation Required!")
            print(f"   Reason: {escalation.reason} (Urgency: {escalation.urgency})")
            print(f"   Action: Notify store manager immediately. Do not auto-reply with bot.")
            response_action = {
                "action": "ESCALATE_TO_HUMAN",
                "urgency": escalation.urgency,
                "reason": escalation.reason,
                "notify_admin_message": f"تنبيه زبون غاضب/نزاع: {incoming_text}",
                "guideline": escalation.guideline,
            }
        else:
            # 2. Step 2: Extract Algerian facts and build agent context
            agent_ctx = build_agent_context(incoming_text, store_name="Bazar El Djazair")
            system_prompt = format_agent_system_prompt(agent_ctx)

            facts = agent_ctx["grounded_facts"]
            print(f"🎯 Intent: {agent_ctx['intent']['intent']}")
            print(f"🗺️ Dialect: {agent_ctx['dialect']['region']}")
            print(f"📍 Wilayas/Communes: {facts['wilayas']}")
            print(f"📦 Quantities: {facts['quantities']}")
            print(f"🎨 Attributes: {facts['product_attributes']}")
            print(f"📞 Phones: {facts['phones']}")

            response_action = {
                "action": "AI_AUTO_REPLY",
                "intent": agent_ctx["intent"]["intent"],
                "dialect": agent_ctx["dialect"]["region"],
                "extracted_order": {
                    "wilayas": facts["wilayas"],
                    "quantities": facts["quantities"],
                    "attributes": facts["product_attributes"],
                    "phones": facts["phones"],
                    "prices_dzd": facts["prices_dzd"],
                },
                "system_prompt_for_llm": system_prompt,
            }

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(response_action, ensure_ascii=False, indent=2).encode("utf-8"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    server = HTTPServer(("0.0.0.0", port), WhatsAppWebhookHandler)
    print(f"🟢 Algerian E-Commerce WhatsApp Bot Webhook listening on port {port}...")
    print(f"👉 Test endpoint: POST http://localhost:{port}/ with JSON {{\"text\": \"...\"}}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down webhook...")
