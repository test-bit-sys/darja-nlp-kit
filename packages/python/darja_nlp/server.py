"""
Zero-dependency HTTP Microservice Server for Algerian Darja NLP.
Ideal for n8n, Make.com, Flowise, local Docker containers, and webhooks.
Uses standard library http.server only.
"""
from __future__ import annotations

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict
from urllib.parse import urlparse

from .normalizer import normalize
from .arabizi import arabizi_to_arabic
from .sentiment import analyze_sentiment
from .entities import extract_entities, get_wilayas, get_wilaya_by_code
from .quantities import extract_quantities, extract_product_attributes
from .escalation import detect_escalation
from .dialect import detect_dialect
from .intent import identify_intent
from .agent import build_agent_context, format_agent_system_prompt


class DarjaRequestHandler(BaseHTTPRequestHandler):
    """Zero-dependency HTTP request handler with CORS support."""

    def _set_cors_headers(self, status: int = 200, content_type: str = "application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_OPTIONS(self):
        self._set_cors_headers(204)

    def _read_json_body(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(body)
        except Exception:
            return {}

    def _send_json(self, data: Any, status: int = 200):
        self._set_cors_headers(status)
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))

    def _send_error(self, message: str, status: int = 400):
        self._send_json({"error": message}, status=status)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path in ("", "/api", "/api/health"):
            self._send_json({
                "service": "darja-nlp-kit",
                "status": "online",
                "version": "1.0.0",
                "endpoints": [
                    "POST /api/parse",
                    "POST /api/intent",
                    "POST /api/sentiment",
                    "POST /api/dialect",
                    "POST /api/escalation",
                    "POST /api/quantities",
                    "POST /api/agent-context",
                    "GET  /api/wilayas",
                    "GET  /api/wilayas/<code_1_to_69>",
                ]
            })
        elif path == "/api/wilayas":
            wilayas = get_wilayas()
            self._send_json({
                "count": len(wilayas),
                "wilayas": [
                    {
                        "code": w.code,
                        "code_str": w.code_str,
                        "name_ar": w.name_ar,
                        "name_fr": w.name_fr,
                        "region": w.region,
                        "communes_sample": w.communes_sample,
                    }
                    for w in wilayas
                ]
            })
        elif path.startswith("/api/wilayas/"):
            param = path.split("/")[-1]
            if param.isdigit():
                w = get_wilaya_by_code(int(param))
                if w:
                    self._send_json({
                        "code": w.code,
                        "code_str": w.code_str,
                        "name_ar": w.name_ar,
                        "name_fr": w.name_fr,
                        "region": w.region,
                        "communes_sample": w.communes_sample,
                        "communes_fr_sample": w.communes_fr_sample,
                    })
                else:
                    self._send_error(f"Wilaya {param} not found (must be 1-69)", 404)
            else:
                self._send_error("Invalid wilaya code (expected integer 1-69)", 400)
        else:
            self._send_error("Endpoint not found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self._read_json_body()
        text = body.get("text", "")

        if not text and path != "/api/agent-context":
            self._send_error("Field 'text' is required in JSON body")
            return

        if path == "/api/parse":
            entities = extract_entities(text)
            self._send_json({
                "input": text,
                "wilayas": [
                    {
                        "code": w.code,
                        "code_str": w.code_str,
                        "name_ar": w.name_ar,
                        "name_fr": w.name_fr,
                        "region": w.region,
                        "commune": w.commune,
                    }
                    for w in entities.wilayas
                ],
                "prices": [
                    {"raw": p.raw, "amount": p.amount, "currency": p.currency}
                    for p in entities.prices
                ],
                "phones": [
                    {
                        "raw": ph.raw,
                        "normalized": ph.normalized,
                        "operator": ph.operator,
                        "operator_label": ph.operator_label,
                        "formatted": ph.formatted,
                        "whatsapp_url": ph.whatsapp_url,
                    }
                    for ph in entities.phones
                ],
                "payments": [{"raw": p.raw, "method": p.method, "label": p.label} for p in entities.payments],
                "deliveries": [{"raw": d.raw, "company": d.company, "label": d.label} for d in entities.deliveries],
                "delivery_mode": {
                    "raw": entities.delivery_mode.raw,
                    "mode": entities.delivery_mode.mode,
                    "label": entities.delivery_mode.label,
                } if entities.delivery_mode else None,
                "quantities": [
                    {"raw": q.raw, "value": q.value, "unit": q.unit}
                    for q in (entities.quantities or [])
                ],
                "attributes": {
                    "colors": entities.attributes.colors if entities.attributes else [],
                    "sizes": entities.attributes.sizes if entities.attributes else [],
                },
            })
        elif path == "/api/intent":
            res = identify_intent(text)
            self._send_json({
                "input": text,
                "intent": res.intent,
                "confidence": res.confidence,
                "matched_keywords": res.matched_keywords,
                "all_scores": res.all_scores,
            })
        elif path == "/api/sentiment":
            res = analyze_sentiment(text)
            self._send_json({
                "input": text,
                "label": res.label,
                "score": res.score,
                "positive_words": res.positive_words,
                "negative_words": res.negative_words,
            })
        elif path == "/api/dialect":
            res = detect_dialect(text)
            self._send_json({
                "input": text,
                "region": res.region,
                "confidence": res.confidence,
                "detected_markers": res.detected_markers,
                "scores": res.scores,
            })
        elif path == "/api/escalation":
            res = detect_escalation(text)
            self._send_json({
                "input": text,
                "needs_escalation": res.needs_escalation,
                "reason": res.reason,
                "urgency": res.urgency,
                "matched_keywords": res.matched_keywords,
                "guideline": res.guideline,
            })
        elif path == "/api/quantities":
            quants = extract_quantities(text)
            attrs = extract_product_attributes(text)
            self._send_json({
                "input": text,
                "quantities": [{"raw": q.raw, "value": q.value, "unit": q.unit} for q in quants],
                "attributes": {"colors": attrs.colors, "sizes": attrs.sizes},
            })
        elif path == "/api/agent-context":
            store_name = body.get("store_name", "Bazar El Djazair")
            ctx = build_agent_context(text, store_name=store_name)
            system_prompt = format_agent_system_prompt(ctx)
            self._send_json({
                "context": ctx,
                "formatted_system_prompt": system_prompt,
            })
        elif path == "/api/normalize":
            self._send_json({"input": text, "normalized": normalize(text)})
        elif path == "/api/arabizi":
            self._send_json({"input": text, "arabic": arabizi_to_arabic(text)})
        else:
            self._send_error(f"Endpoint '{path}' not found", 404)

    def log_message(self, format: str, *args: Any):
        """Clean log output."""
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def start_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Start the zero-dependency Algerian NLP microservice."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, DarjaRequestHandler)
    print(f"🚀 darja-nlp-kit Microservice running on http://{host}:{port}")
    print(f"📦 Ready for n8n, Make.com, webhooks, and local AI automations.")
    print("Endpoints:")
    print(f"  • GET  http://{host}:{port}/api/health")
    print(f"  • GET  http://{host}:{port}/api/wilayas")
    print(f"  • POST http://{host}:{port}/api/parse")
    print(f"  • POST http://{host}:{port}/api/intent")
    print(f"  • POST http://{host}:{port}/api/sentiment")
    print(f"  • POST http://{host}:{port}/api/dialect")
    print(f"  • POST http://{host}:{port}/api/escalation")
    print(f"  • POST http://{host}:{port}/api/agent-context")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()
