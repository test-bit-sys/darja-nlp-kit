"""
Command-Line Interface (CLI) for darja-nlp-kit.

Usage examples:
  darja-nlp parse "نحوس على 2 حبات مقاس XL نبعثهم لوهران 0661234567"
  darja-nlp intent "شحال التوصيل لسطيف؟"
  darja-nlp escalation "سراقين حشيتوهالي رجعولي دراهمي"
  darja-nlp sentiment "سلعة بزاف شابة يعطيكم الصحة"
  darja-nlp dialect "ارواح درك شوف الغاية"
  darja-nlp server --port 8080
"""
from __future__ import annotations

import argparse
import json
import sys

from .normalizer import normalize
from .arabizi import arabizi_to_arabic
from .sentiment import analyze_sentiment
from .entities import extract_entities
from .quantities import extract_quantities, extract_product_attributes
from .escalation import detect_escalation
from .dialect import detect_dialect
from .intent import identify_intent
from .agent import build_agent_context, format_agent_system_prompt
from .server import start_server


def main():
    parser = argparse.ArgumentParser(
        prog="darja-nlp",
        description="Zero-dependency NLP & AI Automation Toolkit for Algerian Darja",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: parse
    p_parse = subparsers.add_parser("parse", help="Extract Algerian entities, wilayas, phones, operator, prices, and quantities")
    p_parse.add_argument("text", help="Algerian text to parse")
    p_parse.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: intent
    p_intent = subparsers.add_parser("intent", help="Identify Algerian customer business intent")
    p_intent.add_argument("text", help="Message text")
    p_intent.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: escalation
    p_esc = subparsers.add_parser("escalation", help="Detect angry customers, legal threats, or human agent requests")
    p_esc.add_argument("text", help="Message text")
    p_esc.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: sentiment
    p_sent = subparsers.add_parser("sentiment", help="Analyze Algerian sentiment (positive, negative, neutral)")
    p_sent.add_argument("text", help="Message text")
    p_sent.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: dialect
    p_dia = subparsers.add_parser("dialect", help="Detect Algerian regional dialect (Center, East, West, South)")
    p_dia.add_argument("text", help="Message text")
    p_dia.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: quantities
    p_qty = subparsers.add_parser("quantities", help="Extract Algerian colloquial quantities and product attributes")
    p_qty.add_argument("text", help="Message text")
    p_qty.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: agent-prompt
    p_prompt = subparsers.add_parser("agent-prompt", help="Build grounded context and system prompt for LLMs (GPT, Claude, Gemini)")
    p_prompt.add_argument("text", help="Customer message")
    p_prompt.add_argument("--store", default="Bazar El Djazair", help="Store name")

    # Command: server
    p_srv = subparsers.add_parser("server", help="Start local zero-dependency HTTP microservice (for n8n, Make, webhooks)")
    p_srv.add_argument("--host", default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
    p_srv.add_argument("--port", type=int, default=8080, help="Port number (default: 8080)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "parse":
        entities = extract_entities(args.text)
        res = {
            "wilayas": [{"code": w.code, "name_ar": w.name_ar, "commune": w.commune} for w in entities.wilayas],
            "prices_dzd": [{"amount": p.amount, "raw": p.raw} for p in entities.prices],
            "phones": [{"normalized": ph.normalized, "operator": ph.operator_label, "whatsapp": ph.whatsapp_url} for ph in entities.phones],
            "quantities": [{"value": q.value, "unit": q.unit, "raw": q.raw} for q in (entities.quantities or [])],
            "attributes": {
                "colors": entities.attributes.colors if entities.attributes else [],
                "sizes": entities.attributes.sizes if entities.attributes else [],
            },
            "delivery": [d.label for d in entities.deliveries],
        }
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print("=== Algerian Entities Extracted ===")
            if res["wilayas"]:
                w_str = ", ".join(f"{w['name_ar']} ({w['code']})" + (f" - بلدية {w['commune']}" if w['commune'] else "") for w in res["wilayas"])
                print(f"📍 Wilayas: {w_str}")
            if res["prices_dzd"]:
                p_str = ", ".join(f"{p['amount']:,} DZD ({p['raw']})" for p in res["prices_dzd"] if p["amount"] is not None)
                print(f"💰 Prices: {p_str}")
            if res["phones"]:
                ph_str = ", ".join(f"{ph['normalized']} [{ph['operator']}]" for ph in res["phones"])
                print(f"📞 Phones: {ph_str}")
            if res["quantities"]:
                q_str = ", ".join(f"{q['value']} {q['unit']} ({q['raw']})" for q in res["quantities"])
                print(f"📦 Quantities: {q_str}")
            if res["attributes"]["colors"] or res["attributes"]["sizes"]:
                print(f"🎨 Attributes: Colors={res['attributes']['colors']}, Sizes={res['attributes']['sizes']}")

    elif args.command == "intent":
        res = identify_intent(args.text)
        data = {
            "intent": res.intent,
            "confidence": res.confidence,
            "matched_keywords": res.matched_keywords,
        }
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"🎯 Intent: {res.intent} (Confidence: {res.confidence:.2f})")
            print(f"🔑 Matched Keywords: {', '.join(res.matched_keywords)}")

    elif args.command == "escalation":
        res = detect_escalation(args.text)
        data = {
            "needs_escalation": res.needs_escalation,
            "reason": res.reason,
            "urgency": res.urgency,
            "guideline": res.guideline,
            "matched_keywords": res.matched_keywords,
        }
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            status = "🚨 ESCALATION REQUIRED" if res.needs_escalation else "✅ NORMAL (No Escalation)"
            print(f"Status: {status}")
            print(f"Reason: {res.reason} | Urgency: {res.urgency}")
            print(f"Guideline: {res.guideline}")
            if res.matched_keywords:
                print(f"Keywords: {', '.join(res.matched_keywords)}")

    elif args.command == "sentiment":
        res = analyze_sentiment(args.text)
        data = {
            "label": res.label,
            "score": res.score,
            "positive_words": res.positive_words,
            "negative_words": res.negative_words,
        }
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            icon = "😊" if res.label == "POSITIVE" else ("😡" if res.label == "NEGATIVE" else "😐")
            print(f"Sentiment: {icon} {res.label} (Score: {res.score:.2f})")
            if res.positive_words:
                print(f"Positive terms: {', '.join(res.positive_words)}")
            if res.negative_words:
                print(f"Negative terms: {', '.join(res.negative_words)}")

    elif args.command == "dialect":
        res = detect_dialect(args.text)
        data = {
            "region": res.region,
            "confidence": res.confidence,
            "detected_markers": res.detected_markers,
        }
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"🗺️ Region: {res.region} (Confidence: {res.confidence:.2f})")
            print(f"Markers: {', '.join(res.detected_markers) if res.detected_markers else 'None'}")

    elif args.command == "quantities":
        quants = extract_quantities(args.text)
        attrs = extract_product_attributes(args.text)
        data = {
            "quantities": [{"value": q.value, "unit": q.unit, "raw": q.raw} for q in quants],
            "attributes": {"colors": attrs.colors, "sizes": attrs.sizes},
        }
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("📦 Quantities:", ", ".join(f"{q.value} {q.unit} ({q.raw})" for q in quants) or "None")
            print(f"🎨 Colors: {', '.join(attrs.colors) or 'None'}")
            print(f"📏 Sizes: {', '.join(attrs.sizes) or 'None'}")

    elif args.command == "agent-prompt":
        ctx = build_agent_context(args.text, store_name=args.store)
        prompt = format_agent_system_prompt(ctx)
        print(prompt)

    elif args.command == "server":
        start_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
