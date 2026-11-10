# luna.europe

**1 code, 1000 pictures, or stories.**

A first public project from the luna.europe creator: help people connect their experience to possible futures, inspect the evidence behind a recommendation, and keep the final decision themselves.

This repository contains a working **local prototype**, not a trained foundation model. It combines an explicit matching rubric, private application review, a JSON API, a minimal MCP server and an interactive 3D architecture diagram. The included profile and job are fictional. Personal application work is kept outside this repository.

## Try it for free

Python 3.11+ is sufficient; the core has no third-party runtime dependencies.

```bash
git clone https://github.com/francosgo/luna-europe-matching.git
cd luna-europe-matching
python -m luna_match.server
```

Open **http://127.0.0.1:8765**. Choose **Review application**, switch between CV and motivation letter, choose **Change it**, edit, save, check the facts and approve. **Print / Save PDF** exports the displayed document through your browser. **Inside the system** opens the rotatable 3D diagram and adjustable `y = wx + b` explanation.

The browser and server must run on the same device. This server intentionally cannot be exposed publicly. Run from this checkout: the Python wheel alone does not include the web UI or examples.

## Bring your own inputs

1. Copy `examples/workspace.json` to `.private/workspace.json`.
2. Replace the fictional evidence with your own facts and source descriptions. Do not paste secrets.
3. Add opportunities with employer URLs, locations, requirements and your assessment: `supported`, `partial`, `gap`, or `unknown`.
4. Add truthful CV and letter drafts. Every supported claim needs evidence. Mark contradictions for review.
5. Restart the server. New document IDs are seeded once; edit existing drafts through the interface so their revision history is preserved.

You can use an external directory with `python -m luna_match.server --data-dir /absolute/private/path`.
The input fields and a complete synthetic example are in [examples/workspace.json](examples/workspace.json).

**Outputs:** evidence fit, assessed coverage, unknown upper bound, mandatory gaps, source references, saved document versions and approvals. Natural-language change requests are stored locally for a connected agent to read and act on. They do not silently invoke an AI provider. Direct edits work immediately. For automatic instruction-based revisions, optionally run your own local Ollama server and start this app with `LUNA_LOCAL_MODEL=your-installed-model python -m luna_match.server`. The additional **Apply with local AI** button sends text only to `127.0.0.1:11434`, saves the result as an unapproved draft and requires factual review. No model is downloaded or enabled by default. This version does not crawl job boards, submit applications, or autonomously retrain.

## The calculation

For requirement `i`, assign evidence `xᵢ ∈ {0, 0.5, 1}` and importance `wᵢ > 0`.

`fit = 100 × Σ(wᵢxᵢ) / Σwᵢ`, with `b = 0`.

Unknowns contribute zero to the conservative score and contribute their full weight to a separate possible upper bound. This is not a statistical confidence interval. Mandatory gaps produce `blocked`; partial or unknown mandatory evidence produces `unresolved`. All other results still require human review. No score is a probability of employment, a measure of human worth, or proof of future wellbeing.

## API and MCP

Use the same scorer directly:

```python
import json
from luna_match.engine import match
payload = json.load(open("examples/match.json"))
print(match(payload))
```

The local HTTP API includes `POST /api/match`, `POST /api/review`, `POST /api/approve`, `POST /api/request` and `GET /api/requests`. Read `/api/workspace` to obtain the local session token; send it as `X-Luna-Token` for writes. See [API.md](docs/API.md).

For an MCP host, configure a stdio process with command `python`, arguments `-m luna_match.mcp`, and working directory set to this checkout. The `explain_match` tool accepts the same payload. It exposes only scoring, not private files or approvals. Its protocol implementation is deliberately minimal; host interoperability is still to be tested.

## Stack, architecture and learning

| Layer | Technology | Why |
|---|---|---|
| Research | Human/agent browser workflow | Check original listings and keep provenance |
| Matching | Python, explicit weighted rubric | Inspect and reproduce every contribution |
| Private memory | SQLite, revision numbers, SHA-256 | Retain changes; prevent stale approvals |
| Review | HTML, CSS, vanilla JavaScript | Easy to read, run and embed without a build |
| Visual explanation | CSS 3D transforms and sliders | Explore flow and the scoring equation |
| Integration | JSON HTTP and MCP stdio | Reuse the same engine in other applications |
| Optional payments | Separate x402 testnet and Stripe sandbox adapters | Isolate financial operations from career documents |

See [architecture](docs/ARCHITECTURE.md), [model card](docs/MODEL_CARD.md), [evaluation and learning](docs/LEARNING.md), [impact framework](docs/IMPACT.md), [payments and business model](docs/PAYMENTS.md), and the [invention record](docs/INVENTION_RECORD.md).

Private revision memory is implemented. Aggregate category-only feedback is opt-in and local; it is not automatically uploaded. Future improvements require a consented evaluation set, controlled experiments and a reviewed version release. No near-zero error claim has been demonstrated.

## Verification

```bash
python -m unittest discover -s tests -v
PYTHONPATH=. python scripts/benchmark.py
node --check web/app.js
node --check web/architecture.js
```

Tests cover evidence validation, unknowns, mandatory gaps, stale approvals, feedback boundaries and MCP tool parity. Local benchmark results describe scoring latency only, not overall agent speed or recommendation accuracy. [Build log](docs/BUILD_LOG.md).

## Reuse, revenue and contribution

The Apache-2.0 license permits commercial use and modification subject to its terms, including applicable notices. It includes a patent grant and does not grant trademark rights. Open-source code remains reusable; using it does not automatically create a subscription to a hosted service. The luna.europe name is an attribution and project identity, not a claim of registered trademark protection. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

The proposed business is an optional hosted API with subscriptions and metered calls. A one-month launch review is proposed for **10 December 2026**; there is no automatic charging timer. Prices, accounts, limits and live settlement require configuration and validation. Fees must not be represented as proven payments for perfect predictions.

Contribute reproducible issues, synthetic test cases, accessibility fixes and source-backed improvements. Explain what changed and why; keep personal records out of issues and commits. This is a decision-support experiment designed to grow through careful evaluation, not the first matching system in the world.

A GitHub Actions template is supplied at `docs/ci/verify.yml`. To enable it, copy it to `.github/workflows/check.yml` using a credential with workflow permission. CI is not enabled automatically.
