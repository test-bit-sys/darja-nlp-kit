"""
FastAPI Microservice Template for Algerian Darja NLP.
Requires: pip install fastapi uvicorn darja-nlp-kit
"""

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:
    print("Notice: 'fastapi' or 'pydantic' not installed. Install with 'pip install fastapi uvicorn'")
    import sys
    sys.exit(0)

import os
import sys

# Ensure local darja_nlp package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages", "python")))

from darja_nlp import (
    build_agent_context,
    detect_escalation,
    extract_entities,
    format_agent_system_prompt,
    identify_intent,
)

app = FastAPI(
    title="Algerian Darja NLP Service",
    description="REST API for parsing Algerian Arabic, Arabizi, Wilayas, and AI agent prompts.",
    version="1.0.0",
)


class TextRequest(BaseModel):
    text: str
    store_name: str = "Bazar El Djazair"


@app.get("/health")
def health():
    return {"status": "ok", "service": "darja-nlp-fastapi"}


@app.post("/parse")
def parse(req: TextRequest):
    entities = extract_entities(req.text)
    intent = identify_intent(req.text)
    escalation = detect_escalation(req.text)
    return {
        "text": req.text,
        "intent": intent.intent,
        "needs_escalation": escalation.needs_escalation,
        "wilayas": [{"code": w.code, "name_ar": w.name_ar, "commune": w.commune} for w in entities.wilayas],
        "phones": [{"normalized": ph.normalized, "operator": ph.operator_label} for ph in entities.phones],
        "prices": [{"amount": p.amount, "raw": p.raw} for p in entities.prices if p.amount is not None],
        "quantities": [{"value": q.value, "unit": q.unit} for q in (entities.quantities or [])],
        "attributes": {
            "colors": entities.attributes.colors if entities.attributes else [],
            "sizes": entities.attributes.sizes if entities.attributes else [],
        },
    }


@app.post("/agent-context")
def agent_context(req: TextRequest):
    ctx = build_agent_context(req.text, store_name=req.store_name)
    prompt = format_agent_system_prompt(ctx)
    return {
        "context": ctx,
        "formatted_system_prompt": prompt,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
