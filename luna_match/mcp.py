"""Minimal newline-delimited MCP stdio server, read-only tools, no HTTP exposure."""
import json
import sys
from .engine import match

SCHEMA = {"type": "object", "properties": {"evidence": {"type": "array", "items": {"type": "object"}},
          "requirements": {"type": "array", "items": {"type": "object"}}}, "required": ["evidence", "requirements"]}

def handle(msg):
    method, params = msg.get("method"), msg.get("params", {})
    if "id" not in msg:
        return None
    result = None
    if method == "initialize":
        result = {"protocolVersion": "2025-11-25", "capabilities": {"tools": {}}, "serverInfo": {"name": "luna-europe", "version": "0.1.0"}}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [{"name": "explain_match", "description": "Score explicit evidence assessments. Does not fetch jobs or make employment decisions.", "inputSchema": SCHEMA}]}
    elif method == "tools/call" and params.get("name") == "explain_match":
        try:
            result = {"content": [{"type": "text", "text": json.dumps(match(params.get("arguments", {})))}]}
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            result = {"isError": True, "content": [{"type": "text", "text": str(e)}]}
    else:
        return {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": msg["id"], "result": result}

def main():
    for line in sys.stdin:
        try:
            if len(line) > 1000000:
                raise ValueError("Message too large")
            reply = handle(json.loads(line))
        except (ValueError, TypeError, AttributeError):
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Invalid message"}}
        if reply is not None:
            print(json.dumps(reply), flush=True)

if __name__ == "__main__":
    main()
