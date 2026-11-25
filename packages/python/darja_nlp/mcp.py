"""Zero-dependency Model Context Protocol (MCP) JSON-RPC 2.0 stdio server for Algerian Darja NLP."""
from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional

from .agent import execute_agent_tool, get_mcp_tool_definitions


def handle_mcp_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process a single JSON-RPC 2.0 MCP request and return the response dict (or None for notifications)."""
    req_id = msg.get("id")
    method = str(msg.get("method") or "")
    params = msg.get("params") or {}

    if req_id is None and method.startswith("notifications/"):
        return None

    if method == "initialize":
        result: Dict[str, Any] = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "darja-nlp-kit", "version": "2.0.0"},
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": get_mcp_tool_definitions()}
    elif method == "tools/call":
        tool_name = str(params.get("name") or "")
        arguments = params.get("arguments") or {}
        tool_out = execute_agent_tool(tool_name, arguments)
        is_err = isinstance(tool_out, dict) and "error" in tool_out and len(tool_out) == 1
        result = {
            "content": [{"type": "text", "text": json.dumps(tool_out, ensure_ascii=False)}],
            "isError": is_err,
        }
    else:
        if req_id is None:
            return None
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    if req_id is None:
        return None
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def run_mcp_server() -> None:
    """Run the darja-nlp-kit MCP stdio transport loop."""
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("[darja-nlp-kit] MCP server ready on stdio (zero-dependency).", file=sys.stderr, flush=True)
    for line in sys.stdin:
        raw = line.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError as exc:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
            print(json.dumps(err_resp, ensure_ascii=False), flush=True)
            continue

        resp = handle_mcp_message(msg)
        if resp is not None:
            print(json.dumps(resp, ensure_ascii=False), flush=True)
