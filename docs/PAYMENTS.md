# Commercial model and payment boundary

The local open-source edition is free. Proposed hosted tiers: a free trial quota, an individual subscription, a team subscription and metered agent calls. Prices are deliberately not committed. Review launch economics on 10 December 2026; nothing starts charging automatically.

## Included code

* `payments/x402-sandbox.mjs`: optional x402 development adapter for `POST /v1/match`; Base Sepolia, test funds, nominal $0.01 test price. Calls the same Python scorer in a bounded subprocess. Requires a developer's own CDP credentials and receiving address. The SDK performs payment protocol handling; a plain request header is never treated as proof of payment by application code.
* `payments/stripe_sandbox.py`: Stripe test-mode subscription Checkout creation with an idempotency key, plus timestamped raw-body webhook signature verification. It rejects live keys and live events. It does not provide hosted checkout pages or grant entitlements.

**These are separate sandbox adapters. A Stripe-settled x402 path is not implemented or verified.** Stripe documents machine payments including x402, but account access and supported integration APIs must be established before wiring that specific rail. No wallets, Stripe products, prices, subscriptions or transactions were created by this build.

Optional x402 dependencies (Node 22+): `express`, `@coinbase/cdp-sdk`, `@x402/express`, `@x402/core`, `@x402/evm`, `@x402/svm`, `@x402/extensions`. Follow the upstream SDK's current compatibility guidance; do not use this unverified sandbox adapter for mainnet funds. Install in `payments/`, set `CDP_API_KEY_ID`, `CDP_API_KEY_SECRET`, `X402_PAY_TO` and start `node payments/x402-sandbox.mjs` from the repository root.

## Before hosted charging

Configure merchant identity, supported country/currencies, approved price IDs, cancellation/refunds and spend caps. Verify a real sandbox end-to-end flow: quote → consent/budget → verify → settle → receipt → entitlement → meter. Reject forged or replayed proofs; bind requests to a tenant/resource and amount. Store unique payment event IDs transactionally to prevent duplicate grants. Handle chargebacks, subscription changes, settlement timeouts and reconciliation without double charges. Test webhook replay and secret rotation. Do not grant service from a browser success redirect alone.

Agents may only spend within owner-defined limits. A successful match score is not a financial win and is not an authorised debit. Performance fees would need a separately agreed outcome definition, attribution rules and dispute process. Payment tokens are money; inference tokens are compute units. Revenue can fund evaluation but does not automatically cause learning.

Sources checked 10 November 2026: [Stripe software-provider guide](https://stripe.com/guides/agentic-commerce-primer-software-providers), [Stripe machine-payments overview](https://stripe.com/blog/machine-payments-protocol), [Coinbase x402 seller quickstart](https://docs.cdp.coinbase.com/x402/seller/quickstart), [Stripe Checkout](https://docs.stripe.com/payments/checkout), [Stripe webhook signatures](https://docs.stripe.com/webhooks/signature).
