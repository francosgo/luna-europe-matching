# Initial build record — 10 November 2026

1. Located and visually verified the intended source CV and role-specific letter in a private workspace.
2. Reviewed the user's digital portfolio. Documented inconsistent dates/titles and separated academic cases from employment.
3. Researched current employer listings across Europe, international remote, US and Singapore/APAC. Kept links, dates and exclusions privately.
4. Prepared five tailored application pairs with evidence-based wording and eight comparison roles. Personal outputs are excluded from this repository.
5. Implemented deterministic matching, mandatory constraints, evidence lookup, private revisions, exact-version approval, direct editing, pending agent requests and category-only feedback.
6. Added a local HTTP API, minimal MCP stdio scorer and interactive 3D architecture/equation explanation.
7. Added separate optional x402 testnet and Stripe sandbox code. No real financial transaction or completed provider integration is claimed.
8. Added Apache-2.0 licensing, provenance map, API/architecture/model/learning/impact/payment documentation and a GitHub CI template.

## Verification

Core suite: 13 tests passed on Python 3.14.7. JavaScript syntax checks passed for UI, architecture and optional payment adapter. A connection-lifecycle warning found during testing was fixed by closing SQLite connections explicitly.

Local benchmark: 1,000 synthetic three-requirement calls, median approximately 0.005 ms and p95 approximately 0.0053 ms. This measures only the scorer, not browsing, document drafting, AI inference, UI interaction or end-to-end workflow. It is not an accuracy benchmark. There are no trained-model token counts: the core does not call an LLM. Exact conversation-wide model token use and monetary cost are unavailable here.

Browser/API/PDF checks and publication results are recorded below after execution. Payment network tests require account-specific sandbox configuration. External MCP-host interoperability, load testing, production deployment and empirical recommendation quality remain unverified.

Browser checks: all eight cards rendered in Chromium; mobile viewport had no horizontal overflow. Ten PDFs exported (five CV/letter pairs); representative CV has two A4 pages and letter one. Rotatable architecture and equation rendered. A low-contrast diagram label found during visual inspection was corrected. Optional local-model adapter has mocked tests; no local model inference was run.

Final local checks: synthetic browser edit → save → approve passed. HTTP rejected missing write token and foreign Origin, and returned 404 for .git/config. PDF dialog clipping was fixed using a standalone print surface and all ten PDFs were regenerated. Public-source personal-data scan found no CV/contact content. Existing francosgo/luna-europe is private, so this project uses the separate public repository luna-europe-matching.

Publication note: GitHub OAuth token does not have workflow scope. The equivalent CI configuration is provided as docs/ci/verify.yml; copy it to .github/workflows/check.yml with a workflow-authorized credential to enable hosted checks. Local tests passed; hosted Actions checks are not enabled.
