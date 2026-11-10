// Optional development adapter. Requires a receiving address and CDP test credentials.
// No Stripe settlement is implied: Stripe and CDP are separate rails in this prototype.
import express from "express";
import { createX402Server } from "@coinbase/cdp-sdk/x402";
import { paymentMiddlewareFromHTTPServer } from "@x402/express";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const payTo = process.env.X402_PAY_TO;
if (!/^0x[0-9a-fA-F]{40}$/.test(payTo || ""))
  throw Error("Set X402_PAY_TO to your test receiving address");
if (!process.env.CDP_API_KEY_ID || !process.env.CDP_API_KEY_SECRET)
  throw Error("CDP credentials required");
const app = express();
app.disable("x-powered-by");
app.use(express.json({ limit: "100kb" }));
// Validate and calculate before requesting payment. No private document store is reachable.
app.post("/v1/match", (req, res, next) => {
  const child = spawn(
    process.env.PYTHON_BIN || "python",
    ["-m", "luna_match.cli"],
    {
      cwd: fileURLToPath(new URL("..", import.meta.url)),
      stdio: ["pipe", "pipe", "ignore"],
    },
  );
  let output = "";
  const timer = setTimeout(() => child.kill(), 5000);
  child.stdout.on("data", (chunk) => {
    output += chunk;
    if (output.length > 200000) child.kill();
  });
  child.on("error", () => {
    clearTimeout(timer);
    if (!res.headersSent) res.status(503).json({ error: "Scorer unavailable" });
  });
  child.on("close", (code) => {
    clearTimeout(timer);
    if (res.headersSent) return;
    try {
      const value = JSON.parse(output);
      if (code !== 0) return res.status(400).json(value);
      res.locals.match = value;
      next();
    } catch {
      res.status(503).json({ error: "Scorer failed" });
    }
  });
  child.stdin.on("error", () => {});
  child.stdin.end(JSON.stringify(req.body));
});
const server = await createX402Server({
  environment: "development",
  payToConfig: { type: "address", evm: payTo },
  routes: {
    "POST /v1/match": {
      price: "$0.01",
      networks: ["eip155:84532"],
      description: "Evidence-based matching, synthetic test use",
    },
  },
});
app.use(paymentMiddlewareFromHTTPServer(server));
app.post("/v1/match", (_req, res) => res.json(res.locals.match));
app.use((_req, res) => res.status(404).json({ error: "Not found" }));
app.listen(8402, "127.0.0.1", () =>
  console.log("x402 TESTNET adapter on http://127.0.0.1:8402"),
);
