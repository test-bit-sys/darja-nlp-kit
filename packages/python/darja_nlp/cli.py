"""
Command-Line Interface (CLI) for darja-nlp-kit.

Usage examples:
  darja-nlp analyze "salam kho rani hab nchrih b 2 mlayen l wahran 0661234567"
  darja-nlp parse "نحوس على 2 حبات مقاس XL نبعثهم لوهران 0661234567"
  darja-nlp intent "شحال التوصيل لسطيف؟"
  darja-nlp escalation "سراقين حشيتوهالي رجعولي دراهمي"
  darja-nlp sentiment "سلعة بزاف شابة يعطيكم الصحة"
  darja-nlp chat "wach ya khoy"
  darja-nlp eval
  darja-nlp server --port 8080
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .normalizer import normalize
from .arabizi import arabizi_to_arabic
from .sentiment import analyze_sentiment
from .entities import extract_entities
from .quantities import extract_quantities, extract_product_attributes
from .escalation import detect_escalation
from .dialect import detect_dialect
from .intent import identify_intent
from .cultural import detect_cultural_references, detect_memes
from .dialogue import respond_to_darja
from .profanity import detect_profanity, censor_profanity
from .pipeline import analyze as run_analyze
from .agent import DarjaAIAgent, LLM_PROVIDERS, build_agent_context, format_agent_system_prompt
from .mcp import run_mcp_server
from .server import start_server


def main():
    parser = argparse.ArgumentParser(
        prog="darja-nlp",
        description="Zero-dependency NLP & AI Automation Toolkit for Algerian Darja",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: analyze (All-in-one)
    p_analyze = subparsers.add_parser("analyze", help="Run complete end-to-end NLP analysis on Darja text")
    p_analyze.add_argument("text", help="Algerian Darja / Arabizi text to analyze")
    p_analyze.add_argument("--persona", choices=["casual", "merchant", "assistant"], default="casual")
    p_analyze.add_argument("--mode", choices=["hybrid", "lexicon", "ml"], default="hybrid")
    p_analyze.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: normalize
    p_norm = subparsers.add_parser("normalize", help="Normalize Arabic/Arabizi Darja text")
    p_norm.add_argument("text", help="Text to normalize")
    p_norm.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: arabizi
    p_arab = subparsers.add_parser("arabizi", help="Convert Arabizi text to Arabic script")
    p_arab.add_argument("text", help="Arabizi text to transliterate")
    p_arab.add_argument("--json", action="store_true", help="Output raw JSON")

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
    p_sent = subparsers.add_parser("sentiment", help="Analyze Algerian sentiment (POSITIVE, NEGATIVE, NEUTRAL, MIXED)")
    p_sent.add_argument("text", help="Message text")
    p_sent.add_argument("--mode", choices=["hybrid", "lexicon", "ml"], default="hybrid", help="Analysis engine mode")
    p_sent.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: dialect
    p_dia = subparsers.add_parser("dialect", help="Detect Algerian regional dialect (Center, East, West, South)")
    p_dia.add_argument("text", help="Message text")
    p_dia.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: quantities
    p_qty = subparsers.add_parser("quantities", help="Extract Algerian colloquial quantities and product attributes")
    p_qty.add_argument("text", help="Message text")
    p_qty.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: culture
    p_cult = subparsers.add_parser("culture", help="Detect Algerian proverbs, viral memes, landmarks, dishes, and slang")
    p_cult.add_argument("text", help="Message or expression text")
    p_cult.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: agent-prompt
    p_prompt = subparsers.add_parser("agent-prompt", help="Build grounded context and system prompt for LLMs (GPT, Claude, Gemini)")
    p_prompt.add_argument("text", help="Customer message")
    p_prompt.add_argument("--store", default="Bazar El Djazair", help="Store name")

    # Command: agent (interactive or single-turn plug-and-play AI Agent)
    p_agent = subparsers.add_parser("agent", help="Run plug-and-play Algerian Darja AI Agent (offline or OpenAI/Gemini/Groq/Ollama)")
    p_agent.add_argument("text", nargs="*", help="Optional message (omit to start interactive terminal chat)")
    p_agent.add_argument("--provider", choices=["offline", *LLM_PROVIDERS.keys()], default=None, help="LLM provider (default: auto/offline)")
    p_agent.add_argument("--model", default=None, help="Optional model override")
    p_agent.add_argument("--api-key", default=None, help="Optional API key (or set DARJA_API_KEY / OPENAI_API_KEY)")
    p_agent.add_argument("--base-url", default=None, help="Custom OpenAI-compatible base URL")
    p_agent.add_argument("--store", default="Bazar El Djazair", help="Store name")
    p_agent.add_argument("--persona", choices=["casual", "merchant", "assistant"], default="merchant")
    p_agent.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: mcp (stdio Model Context Protocol server)
    subparsers.add_parser("mcp", help="Start zero-dependency MCP stdio server for Claude, Cursor, VS Code, or Antigravity")

    # Command: agent-setup (1-step installation & MCP config helper)
    p_setup = subparsers.add_parser("agent-setup", help="Generate plug-and-play MCP config and quickstart guide for AI clients")
    p_setup.add_argument("--client", choices=["generic", "claude", "cursor", "vscode", "antigravity"], default="generic")
    p_setup.add_argument("--out", default=None, help="Optional file path to write MCP JSON configuration")
    p_setup.add_argument("--json", action="store_true", help="Print only the MCP JSON configuration")

    # Command: chat
    p_chat = subparsers.add_parser("chat", help="Generate natural Algerian Darja response (e.g. 'wach ya khoy' -> 'we cv')")
    p_chat.add_argument("text", help="Algerian message or greeting")
    p_chat.add_argument("--persona", choices=["casual", "merchant", "assistant"], default="casual", help="Persona style")
    p_chat.add_argument("--script", choices=["auto", "arabizi", "arabic"], default="auto", help="Output script")
    p_chat.add_argument("--strategy", choices=["auto", "rules", "retrieval"], default="auto", help="Reply strategy")
    p_chat.add_argument("--vary", action="store_true", help="Vary responses instead of picking the top deterministic reply")
    p_chat.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: moderate
    p_mod = subparsers.add_parser("moderate", help="Detect profanities, toxic slurs, and censor Algerian text")
    p_mod.add_argument("text", help="Message to inspect")
    p_mod.add_argument("--mask", default="***", help="Mask replacement string")
    p_mod.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: memes
    p_meme = subparsers.add_parser("memes", help="Detect Algerian viral memes and TV comedy quotes")
    p_meme.add_argument("text", help="Text containing meme or quote")
    p_meme.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: eval
    p_eval = subparsers.add_parser("eval", help="Evaluate toolkit sentiment accuracy on real held-out Algerian benchmark")
    p_eval.add_argument("--mode", choices=["hybrid", "lexicon", "ml"], default="hybrid")
    p_eval.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: server
    p_srv = subparsers.add_parser("server", help="Start local zero-dependency HTTP microservice (for n8n, Make, webhooks)")
    p_srv.add_argument("--host", default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
    p_srv.add_argument("--port", type=int, default=8080, help="Port number (default: 8080)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "analyze":
        report = run_analyze(args.text, persona=args.persona, sentiment_mode=args.mode)
        data = report.to_dict()
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("=== Darja NLP Unified Analysis ===")
            print(f"Normalized : {report.normalized}")
            if report.arabic != report.raw_text:
                print(f"Arabic     : {report.arabic}")
            if report.sentiment:
                print(f"Sentiment  : {report.sentiment.label} ({report.sentiment.score:+.2f}) [{report.sentiment.method}]")
            if report.intent:
                print(f"Intent     : {report.intent.intent} ({report.intent.confidence:.2f})")
            if report.dialect:
                print(f"Dialect    : {report.dialect.region} ({report.dialect.confidence:.2f})")
            if report.entities and report.entities.wilayas:
                print("Wilayas    :", ", ".join(f"{w.name_ar} ({w.code})" for w in report.entities.wilayas))
            if report.entities and report.entities.prices:
                print("Prices DZD :", ", ".join(f"{p.amount:,.0f}" for p in report.entities.prices if p.amount is not None))
            if report.entities and report.entities.phones:
                print("Phones     :", ", ".join(p.normalized for p in report.entities.phones))
            if report.profanity and report.profanity.is_profane:
                print(f"Moderation : PROFANE ({report.profanity.severity}) -> {report.profanity.censored_text}")
            if report.reply:
                print(f"Reply      : {report.reply.reply} [{report.reply.source}]")

    elif args.command == "normalize":
        res = normalize(args.text)
        if args.json:
            print(json.dumps({"input": args.text, "normalized": res}, ensure_ascii=False, indent=2))
        else:
            print(res)

    elif args.command == "arabizi":
        res = arabizi_to_arabic(args.text)
        if args.json:
            print(json.dumps({"input": args.text, "arabic": res}, ensure_ascii=False, indent=2))
        else:
            print(res)

    elif args.command == "parse":
        entities = extract_entities(args.text)
        cult = detect_cultural_references(args.text)
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
            "cultural": {
                "has_cultural_reference": cult.has_cultural_reference,
                "summary": cult.cultural_summary if cult.has_cultural_reference else None,
            },
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
            if cult.has_cultural_reference:
                print(f"🏛️ Culture/Slang: {cult.cultural_summary}")

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
            "matched_triggers": res.matched_triggers,
        }
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            status = "ESCALATION REQUIRED" if res.needs_escalation else "NORMAL (No Escalation)"
            print(f"Status: {status}")
            print(f"Reason: {res.reason} | Urgency: {res.urgency}")
            print(f"Guideline: {res.guideline}")
            if res.matched_triggers:
                print(f"Triggers: {', '.join(res.matched_triggers)}")

    elif args.command == "sentiment":
        res = analyze_sentiment(args.text, mode=args.mode)
        data = {
            "label": res.label,
            "score": res.score,
            "method": res.method,
            "probabilities": res.probabilities,
            "positive_tokens": res.positive_tokens,
            "negative_tokens": res.negative_tokens,
            "negated": res.negated,
        }
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"Sentiment: {res.label} (Score: {res.score:+.2f}, Method: {res.method})")
            if res.positive_tokens:
                print(f"Positive terms: {', '.join(res.positive_tokens)}")
            if res.negative_tokens:
                print(f"Negative terms: {', '.join(res.negative_tokens)}")

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

    elif args.command == "culture":
        cult = detect_cultural_references(args.text)
        data = {
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
        }
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("=== Algerian Cultural References & Slang ===")
            print(f"Has Reference : {'Yes' if data['has_cultural_reference'] else 'No'}")
            print(f"Summary       : {data['cultural_summary']}")
            if data["proverbs"]:
                print(f"Proverbs      : {', '.join(p['canonical_name'] for p in data['proverbs'])}")
            if data["memes_and_trends"]:
                print(f"Memes/Trends  : {', '.join(m['canonical_name'] for m in data['memes_and_trends'])}")
            if data["landmarks"]:
                print(f"Landmarks     : {', '.join(l['canonical_name'] for l in data['landmarks'])}")
            if data["gastronomy"]:
                print(f"Gastronomy    : {', '.join(g['canonical_name'] for g in data['gastronomy'])}")
            if data["slang_expressions"]:
                print(f"Slang Terms   : {', '.join(s['canonical_name'] for s in data['slang_expressions'])}")

    elif args.command == "chat":
        res = respond_to_darja(
            args.text,
            persona=args.persona,
            script=args.script,
            strategy=args.strategy,
            vary=args.vary,
        )
        data = {
            "reply": res.reply,
            "intent": res.intent,
            "script": res.script,
            "confidence": res.confidence,
            "matched_pattern": res.matched_pattern,
            "source": res.source,
        }
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("=== Algerian Conversational Response ===")
            print(f"Reply          : {res.reply}")
            print(f"Intent         : {res.intent}")
            print(f"Script         : {res.script}")
            print(f"Source         : {res.source}")
            print(f"Confidence     : {res.confidence:.2f}")

    elif args.command == "moderate":
        res = detect_profanity(args.text)
        censored = censor_profanity(args.text, mask=args.mask)
        data = {
            "is_profane": res.is_profane,
            "severity": res.severity,
            "matches_count": len(res.matches),
            "matches": [
                {"term": m.term, "category": m.category, "severity": m.severity, "matched_text": m.matched_text}
                for m in res.matches
            ],
            "censored_text": censored,
        }
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("=== Content Moderation & Profanity Check ===")
            print(f"Is Profane     : {'Yes' if res.is_profane else 'No'}")
            print(f"Severity       : {res.severity.upper()}")
            print(f"Matches        : {len(res.matches)}")
            print(f"Censored Text  : {censored}")

    elif args.command == "memes":
        memes = detect_memes(args.text)
        data = [
            {"phrase": m.canonical_name, "meaning": m.meaning, "metadata": m.metadata}
            for m in memes
        ]
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("=== Algerian Memes & Pop-Culture ===")
            if not memes:
                print("No viral memes detected in text.")
            for m in memes:
                print(f"Meme: {m.canonical_name}")
                print(f"  Meaning: {m.meaning}")
                if m.metadata.get("origin"):
                    print(f"  Origin : {m.metadata['origin']}")

    elif args.command == "eval":
        bench_path = Path(__file__).resolve().parent / "data" / "eval_benchmark.json"
        if not bench_path.exists():
            print("Error: eval_benchmark.json not found in package data.", file=sys.stderr)
            sys.exit(1)
        bench = json.loads(bench_path.read_text(encoding="utf-8")).get("sentiment", [])
        by_src = {}
        ok = 0
        for row in bench:
            pred = analyze_sentiment(row["text"], mode=args.mode).label
            if pred == "MIXED":
                pred = "NEUTRAL"
            src = row.get("source", "unknown")
            by_src.setdefault(src, [0, 0])
            by_src[src][1] += 1
            if pred == row["label"]:
                ok += 1
                by_src[src][0] += 1
        summary = {
            "mode": args.mode,
            "total": len(bench),
            "correct": ok,
            "accuracy": round(ok / len(bench), 4) if bench else 0.0,
            "by_source": {k: {"correct": v[0], "total": v[1], "accuracy": round(v[0] / v[1], 4)} for k, v in by_src.items()},
        }
        if args.json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(f"=== Held-Out Sentiment Benchmark (mode={args.mode}) ===")
            print(f"Overall Accuracy : {ok}/{len(bench)} ({summary['accuracy']:.2%})")
            for src, stats in summary["by_source"].items():
                print(f"  - {src:20s}: {stats['correct']}/{stats['total']} ({stats['accuracy']:.2%})")

    elif args.command == "agent-prompt":
        ctx = build_agent_context(args.text, store_name=args.store)
        prompt = format_agent_system_prompt(ctx)
        print(prompt)

    elif args.command == "agent":
        agent = DarjaAIAgent(
            store_name=args.store,
            persona=args.persona,
            provider=args.provider,
            api_key=args.api_key,
            model=args.model,
            base_url=args.base_url,
        )
        msg_text = " ".join(args.text).strip()
        if msg_text:
            res = agent.ask(msg_text)
            if args.json:
                print(json.dumps({
                    "reply": res.reply,
                    "provider": res.provider,
                    "model": res.model,
                    "intent": res.intent,
                    "dialect": res.dialect,
                    "needs_escalation": res.needs_escalation,
                    "ready_to_confirm": res.ready_to_confirm,
                    "missing_slots": res.missing_slots,
                    "slots": res.slots,
                    "tool_calls_executed": res.tool_calls_executed,
                }, ensure_ascii=False, indent=2))
            else:
                print(f"[{res.provider}:{res.model}] ({res.intent} | {res.dialect})")
                print(f"Agent > {res.reply}")
                if res.missing_slots and not res.needs_escalation:
                    print(f"Slots missing: {', '.join(res.missing_slots)}")
        else:
            print(f"=== DarjaAIAgent Interactive Chat ({agent.provider}:{agent.model}) ===")
            print("Type customer messages in Arabic/Arabizi. Commands: /slots, /reset, /exit")
            while True:
                try:
                    line = input("You > ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                if not line:
                    continue
                if line in ("/exit", "exit", "quit"):
                    break
                if line == "/reset":
                    agent.reset()
                    print("[session reset]")
                    continue
                if line == "/slots":
                    print(json.dumps(agent.slots, ensure_ascii=False, indent=2))
                    continue
                res = agent.ask(line)
                print(f"Agent [{res.intent}] > {res.reply}")

    elif args.command == "mcp":
        run_mcp_server()

    elif args.command == "agent-setup":
        cfg = DarjaAIAgent.get_mcp_config(runtime="python")
        if args.out:
            out_path = Path(args.out)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(cfg, ensure_ascii=False, indent=2))
        else:
            print(f"=== darja-nlp-kit AI Agent Setup ({args.client}) ===")
            print("1. One-Command Install (Python from GitHub):")
            print('   pip install "git+https://github.com/test-bit-sys/darja-nlp-kit.git#subdirectory=packages/python"')
            print("\n2. MCP Server Config (Claude Desktop / Cursor / VS Code / Antigravity):")
            print(json.dumps(cfg, ensure_ascii=False, indent=2))
            if args.out:
                print(f"\n[SAVED] Wrote MCP config to: {args.out}")
            print("\n3. Quick Terminal AI Agent Chat:")
            print("   darja-nlp agent                          # Offline Algerian Darja Agent")
            print("   darja-nlp agent --provider ollama        # Local Ollama (qwen2.5:7b)")
            print("   darja-nlp agent --provider openai        # GPT-4o-mini (uses OPENAI_API_KEY)")
            print("   darja-nlp agent --provider gemini        # Gemini 2.5 Flash (uses DARJA_API_KEY)")

    elif args.command == "server":
        start_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
