"""
LangChain and OpenAI Tools integration for Algerian Darja NLP.

Shows how to provide Algerian entity extraction, Wilaya database (01-69),
and escalation checks as tools to an LLM agent.
"""

from __future__ import annotations

import json
import os
import sys

# Ensure local darja_nlp package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages", "python")))

from darja_nlp import (
    build_agent_context,
    detect_escalation,
    extract_entities,
    get_openai_tool_definitions,
    get_wilaya_by_code,
)


def run_darja_tool(name: str, arguments: dict) -> str:
    """Execute the corresponding Algerian Darja NLP tool requested by the model."""
    if name == "parse_algerian_message":
        text = arguments.get("text", "")
        entities = extract_entities(text)
        return json.dumps({
            "wilayas": [
                {"code": w.code, "name_ar": w.name_ar, "commune": w.commune}
                for w in entities.wilayas
            ],
            "prices_dzd": [
                {"amount": p.amount, "raw": p.raw}
                for p in entities.prices if p.amount is not None
            ],
            "phones": [
                {"normalized": ph.normalized, "operator": ph.operator_label}
                for ph in entities.phones
            ],
            "quantities": [
                {"value": q.value, "unit": q.unit}
                for q in (entities.quantities or [])
            ],
            "attributes": {
                "colors": entities.attributes.colors if entities.attributes else [],
                "sizes": entities.attributes.sizes if entities.attributes else [],
            },
        }, ensure_ascii=False)

    elif name == "get_wilaya_details":
        code = arguments.get("code")
        if isinstance(code, int):
            w = get_wilaya_by_code(code)
            if w:
                return json.dumps({
                    "code": w.code,
                    "name_ar": w.name_ar,
                    "name_fr": w.name_fr,
                    "region": w.region,
                    "communes_sample": w.communes_sample,
                }, ensure_ascii=False)
        return json.dumps({"error": f"Wilaya {code} not found"}, ensure_ascii=False)

    elif name == "check_human_escalation":
        text = arguments.get("text", "")
        esc = detect_escalation(text)
        return json.dumps({
            "needs_escalation": esc.needs_escalation,
            "reason": esc.reason,
            "urgency": esc.urgency,
            "guideline": esc.guideline,
        }, ensure_ascii=False)

    return json.dumps({"error": f"Unknown tool: {name}"})


def demonstrate_tool_definitions():
    """Print standard OpenAI tool calling schemas."""
    tools = get_openai_tool_definitions()
    print("=== OpenAI / LangChain Tool Schemas for Algerian NLP ===")
    print(json.dumps(tools, ensure_ascii=False, indent=2))

    sample_msg = "حاب نشري زوج حبات كحلة مقاس L ونبعثهم لوهران 0661234567 شحال؟"
    print(f"\nExample: Agent calling 'parse_algerian_message' on:\n\"{sample_msg}\"")
    result = run_darja_tool("parse_algerian_message", {"text": sample_msg})
    print("\nTool Output (JSON to LLM):")
    print(result)


if __name__ == "__main__":
    demonstrate_tool_definitions()
