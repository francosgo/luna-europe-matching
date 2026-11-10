# Local integration contract

Get `http://127.0.0.1:8765/api/workspace`; retain `csrf` in memory. All POSTs require `Content-Type: application/json` and `X-Luna-Token: <csrf>`. Browser Origin must match. A token is local CSRF protection, not SaaS user authentication. Do not publish this endpoint.

| Method/path | Body | Result |
|---|---|---|
| POST /api/match | examples/match.json | score, coverage, upper bound, gaps, rows, latency |
| POST /api/review | document, body, revision, optional note | new draft revision |
| POST /api/approve | document, revision, hash, facts_confirmed:true | approved current revision |
| POST /api/request | document, revision, instruction | pending agent change request |
| GET /api/requests | none | pending requests, private |
| POST /api/feedback | kind, value:0/1, consent:true | stored locally; never transmitted |
| GET /api/feedback/aggregate | none | categories with at least 10 records |

Document identifiers are `<job-id>:cv` and `<job-id>:letter`. An agent consumes a pending request, retrieves the current document, drafts a truthful revision and POSTs `/api/review` with the expected revision. Saving resolves requests for that document; approval remains a human UI action. No automated background agent is bundled.

MCP: `python -m luna_match.mcp`, newline-delimited JSON-RPC over stdio. Supports initialize, initialized notification, ping, tools/list and tools/call. `explain_match` uses the HTTP engine. Host configuration must point its working directory or PYTHONPATH to this checkout. Protocol version: 2025-11-25. Automated tests check internal framing/tool parity; no external host certification is claimed.

Embedders should call `match()` from their own authenticated service, rather than iframe a private localhost session. A hosted edition must keep tenant authorization separate from payment verification; paying does not grant access to someone else's documents.

Optional `POST /api/rewrite`: document, revision, instruction. Requires LUNA_LOCAL_MODEL and a locally served Ollama model. Endpoint fixed to loopback. Returns a new draft; never approves it. Local inference may still hallucinate; review is mandatory. API reference: https://docs.ollama.com/api/generate
