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
from .cultural import (
    detect_cultural_references,
    get_cultural_data,
    get_slang_data,
    get_memes_data,
    get_franco_darja_data,
    detect_memes,
    detect_franco_darja,
)
from .dialogue import respond_to_darja
from .profanity import detect_profanity, censor_profanity
from .agent import build_agent_context, format_agent_system_prompt
from .pipeline import analyze as run_pipeline_analyze


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
                    "POST /api/analyze",
                    "POST /api/batch",
                    "POST /api/parse",
                    "POST /api/intent",
                    "POST /api/sentiment",
                    "POST /api/dialect",
                    "POST /api/escalation",
                    "POST /api/quantities",
                    "POST /api/culture",
                    "POST /api/chat",
                    "POST /api/moderate",
                    "POST /api/memes",
                    "POST /api/franco",
                    "POST /api/normalize",
                    "POST /api/arabizi",
                    "POST /api/agent-context",
                    "GET  /api/wilayas",
                    "GET  /api/wilayas/<code_1_to_69>",
                    "GET  /api/culture",
                    "GET  /api/memes",
                    "GET  /api/franco",
                ],
            })
        elif path == "/api/culture":
            c_data = get_cultural_data()
            s_data = get_slang_data()
            self._send_json({
                "service": "darja-nlp-kit cultural knowledge engine",
                "proverbs_count": len(c_data.get("proverbs", [])),
                "memes_count": len(c_data.get("memes_and_trends", [])),
                "landmarks_count": len(c_data.get("landmarks", [])),
                "gastronomy_count": len(c_data.get("gastronomy", [])),
                "slang_count": len(s_data.get("expressions", [])),
            })
        elif path == "/api/wilayas":
            wilayas = get_wilayas()
            self._send_json({
                "count": len(wilayas),
                "wilayas": [
                    {
                        "code": w.get("code"),
                        "code_str": w.get("code_str"),
                        "name_ar": w.get("name_ar"),
                        "name_fr": w.get("name_fr"),
                        "era": w.get("era"),
                        "communes_sample": w.get("communes_sample", []),
                    }
                    for w in wilayas
                ],
            })
        elif path.startswith("/api/wilayas/"):
            param = path.split("/")[-1]
            if param.isdigit():
                w = get_wilaya_by_code(int(param))
                if w:
                    self._send_json({
                        "code": w.get("code"),
                        "code_str": w.get("code_str"),
                        "name_ar": w.get("name_ar"),
                        "name_fr": w.get("name_fr"),
                        "era": w.get("era"),
                        "phone_code": w.get("phone_code"),
                        "communes_sample": w.get("communes_sample", []),
                        "communes_fr_sample": w.get("communes_fr_sample", []),
                    })
                else:
                    self._send_error(f"Wilaya {param} not found (must be 1-69)", 404)
            else:
                self._send_error("Invalid wilaya code (expected integer 1-69)", 400)
        elif path == "/api/memes":
            self._send_json(get_memes_data())
        elif path == "/api/franco":
            self._send_json(get_franco_darja_data())
        else:
            self._send_error("Endpoint not found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self._read_json_body()

        if path == "/api/batch":
            texts = body.get("texts")
            if not isinstance(texts, list):
                self._send_error("Field 'texts' (array of strings) is required in JSON body")
                return
            tasks = body.get("tasks")
            results = [run_pipeline_analyze(str(t), tasks=tasks).to_dict() for t in texts]
            self._send_json({"count": len(results), "results": results})
            return

        text = body.get("text", "")
        if not text and path != "/api/agent-context":
            self._send_error("Field 'text' is required in JSON body")
            return

        if path == "/api/analyze":
            tasks = body.get("tasks")
            persona = body.get("persona", "casual")
            sentiment_mode = body.get("sentiment_mode", "hybrid")
            report = run_pipeline_analyze(
                text,
                tasks=tasks,
                persona=persona,
                sentiment_mode=sentiment_mode,
            )
            self._send_json(report.to_dict())
        elif path == "/api/parse":
            entities = extract_entities(text)
            cult = detect_cultural_references(text)
            self._send_json({
                "input": text,
                "wilayas": [
                    {
                        "code": w.code,
                        "code_str": w.code_str,
                        "name_ar": w.name_ar,
                        "name_fr": w.name_fr,
                        "matched_text": w.matched_text,
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
                "payments": [
                    {"type": p.type, "label": p.label, "matched_text": p.matched_text}
                    for p in entities.payments
                ],
                "deliveries": [
                    {"company": d.company, "label": d.label, "matched_text": d.matched_text}
                    for d in entities.deliveries
                ],
                "delivery_mode": {
                    "mode": entities.delivery_mode.mode,
                    "label": entities.delivery_mode.label,
                    "matched_text": entities.delivery_mode.matched_text,
                } if entities.delivery_mode else None,
                "quantities": [
                    {"raw": q.raw, "value": q.value, "unit": q.unit}
                    for q in (entities.quantities or [])
                ],
                "attributes": {
                    "colors": entities.attributes.colors if entities.attributes else [],
                    "sizes": entities.attributes.sizes if entities.attributes else [],
                },
                "cultural": {
                    "has_cultural_reference": cult.has_cultural_reference,
                    "summary": cult.cultural_summary if cult.has_cultural_reference else None,
                },
            })
        elif path == "/api/intent":
            res = identify_intent(text)
            self._send_json({
                "input": text,
                "intent": res.intent,
                "confidence": res.confidence,
                "matched_keywords": res.matched_keywords,
            })
        elif path == "/api/sentiment":
            mode = body.get("mode", "hybrid")
            res = analyze_sentiment(text, mode=mode)
            self._send_json({
                "input": text,
                "label": res.label,
                "score": res.score,
                "method": res.method,
                "probabilities": res.probabilities,
                "positive_tokens": res.positive_tokens,
                "negative_tokens": res.negative_tokens,
                "negated": res.negated,
            })
        elif path == "/api/dialect":
            res = detect_dialect(text)
            self._send_json({
                "input": text,
                "region": res.region,
                "confidence": res.confidence,
                "detected_markers": res.detected_markers,
            })
        elif path == "/api/escalation":
            res = detect_escalation(text)
            self._send_json({
                "input": text,
                "needs_escalation": res.needs_escalation,
                "reason": res.reason,
                "urgency": res.urgency,
                "matched_triggers": res.matched_triggers,
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
        elif path in ("/api/culture", "/api/cultural"):
            cult = detect_cultural_references(text)
            self._send_json({
                "input": text,
                "has_cultural_reference": cult.has_cultural_reference,
                "proverbs": [
                    {"canonical_name": p.canonical_name, "meaning": p.meaning, "region": p.metadata.get("region")}
                    for p in cult.proverbs
                ],
                "memes_and_trends": [
                    {"canonical_name": m.canonical_name, "meaning": m.meaning, "tone": m.metadata.get("tone")}
                    for m in cult.memes_and_trends
                ],
                "landmarks": [
                    {"canonical_name": l.canonical_name, "city": l.metadata.get("city"), "wilaya_code": l.metadata.get("wilaya_code"), "description": l.meaning}
                    for l in cult.landmarks
                ],
                "gastronomy": [
                    {"canonical_name": g.canonical_name, "origin": g.metadata.get("origin"), "category": g.metadata.get("category")}
                    for g in cult.gastronomy
                ],
                "slang_expressions": [
                    {"canonical_name": s.canonical_name, "meaning": s.meaning, "polarity": s.metadata.get("polarity")}
                    for s in cult.slang_expressions
                ],
                "cultural_summary": cult.cultural_summary,
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
        elif path == "/api/chat":
            persona = body.get("persona", "casual")
            script = body.get("script", "auto")
            strategy = body.get("strategy", "auto")
            vary = bool(body.get("vary", False))
            res = respond_to_darja(text, persona=persona, script=script, strategy=strategy, vary=vary)
            self._send_json({
                "input": text,
                "reply": res.reply,
                "intent": res.intent,
                "script": res.script,
                "confidence": res.confidence,
                "matched_pattern": res.matched_pattern,
                "source": res.source,
            })
        elif path == "/api/moderate":
            mask = body.get("mask", "***")
            res = detect_profanity(text)
            censored = censor_profanity(text, mask=mask)
            self._send_json({
                "input": text,
                "is_profane": res.is_profane,
                "severity": res.severity,
                "matches": [
                    {"term": m.term, "category": m.category, "severity": m.severity, "matched_text": m.matched_text}
                    for m in res.matches
                ],
                "censored_text": censored,
            })
        elif path == "/api/memes":
            memes = detect_memes(text)
            self._send_json({
                "input": text,
                "memes": [
                    {"phrase": m.canonical_name, "meaning": m.meaning, "metadata": m.metadata}
                    for m in memes
                ],
            })
        elif path == "/api/franco":
            matches = detect_franco_darja(text)
            self._send_json({
                "input": text,
                "matches": matches,
            })
        else:
            self._send_error(f"Endpoint '{path}' not found", 404)

    def log_message(self, format: str, *args: Any):
        """Clean log output."""
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def start_server(host: str = "0.0.0.0", port: int = 8080) -> HTTPServer:
    """Start the zero-dependency Algerian NLP microservice."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, DarjaRequestHandler)
    print(f"darja-nlp-kit Microservice running on http://{host}:{port}")
    print("Ready for n8n, Make.com, webhooks, and local AI automations.")
    print("Endpoints:")
    print(f"  - GET  http://{host}:{port}/api/health")
    print(f"  - GET  http://{host}:{port}/api/wilayas")
    print(f"  - POST http://{host}:{port}/api/analyze")
    print(f"  - POST http://{host}:{port}/api/batch")
    print(f"  - POST http://{host}:{port}/api/parse")
    print(f"  - POST http://{host}:{port}/api/chat")
    print(f"  - POST http://{host}:{port}/api/moderate")
    print(f"  - POST http://{host}:{port}/api/sentiment")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()
    return httpd
