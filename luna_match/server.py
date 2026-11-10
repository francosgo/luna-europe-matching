"""Single-user loopback workspace. No public production deployment."""
import argparse
import json
import mimetypes
import os
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from .engine import match
from .store import Store
from .rewrite import rewrite

ROOT = Path(__file__).resolve().parent.parent

def serve(data_dir, port):
    os.umask(0o077)
    data_dir.mkdir(parents=True, exist_ok=True)
    store = Store(data_dir / "review.sqlite")
    workspace = json.loads((data_dir / "workspace.json" if (data_dir / "workspace.json").exists() else ROOT / "examples/workspace.json").read_text())
    for job in workspace["jobs"]:
        job["match"] = match({"evidence": workspace["evidence"], "requirements": job["requirements"]})
        for kind in ("cv", "letter"):
            store.seed(job["id"] + ":" + kind, job.get(kind, "Draft not prepared."))
    valid_docs = {j["id"] + ":" + k for j in workspace["jobs"] for k in ("cv", "letter")}
    csrf = secrets.token_urlsafe(32)
    host = f"127.0.0.1:{port}"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # No personal request bodies or URLs in logs.

        def respond(self, value, code=200, mime="application/json"):
            body = json.dumps(value).encode() if mime == "application/json" else value
            self.send_response(code)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(body)

        def valid_host(self):
            if self.headers.get("Host") != host:
                self.respond({"error": "Invalid Host"}, 403)
                return False
            return True

        def do_GET(self):
            if not self.valid_host():
                return
            path = urlsplit(self.path).path
            if path == "/api/workspace":
                docs = {d: store.latest(d) for d in valid_docs}
                self.respond({**workspace, "documents": docs, "csrf": csrf, "requests": store.requests(), "local_model_enabled": bool(os.environ.get('LUNA_LOCAL_MODEL'))})
            elif path == "/api/requests":
                self.respond(store.requests())
            elif path == "/api/feedback/aggregate":
                self.respond(store.aggregate())
            elif path == "/portrait.png" and (data_dir / "portrait.png").exists():
                self.respond((data_dir / "portrait.png").read_bytes(), mime="image/png")
            elif path in ("/", "/app.js", "/style.css", "/architecture.html", "/architecture.js"):
                p = ROOT / "web" / ("index.html" if path == "/" else path[1:])
                self.respond(p.read_bytes(), mime=mimetypes.guess_type(str(p))[0] or "text/plain")
            else:
                self.respond({"error": "Not found"}, 404)

        def do_POST(self):
            if not self.valid_host():
                return
            if self.headers.get("Origin") not in (None, f"http://{host}") or self.headers.get("X-Luna-Token") != csrf:
                self.respond({"error": "Invalid session or origin"}, 403)
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 1000000 or self.headers.get("Content-Type", "").split(';')[0] != "application/json":
                    raise ValueError("Expected JSON body under 1 MB")
                data = json.loads(self.rfile.read(size))
                path = urlsplit(self.path).path
                if path in ("/api/review", "/api/approve", "/api/request", "/api/rewrite") and data.get("document") not in valid_docs:
                    raise ValueError("Unknown document")
                if path == "/api/match":
                    self.respond(match(data))
                elif path == "/api/review":
                    self.respond(store.save(data["document"], data["body"], data["revision"], data.get("note", "Direct edit")))
                elif path == "/api/approve":
                    if data.get("facts_confirmed") is not True:
                        raise ValueError("Confirm the facts and dates before approval")
                    self.respond(store.approve(data["document"], data["revision"], data["hash"]))
                elif path == "/api/request":
                    store.request(data["document"], data["revision"], data["instruction"])
                    self.respond({"status": "pending", "message": "Saved for your agent; approval waits for a revision."})
                elif path == "/api/rewrite":
                    doc = store.latest(data['document'])
                    if doc['revision'] != data['revision']:
                        raise ValueError('Revision conflict')
                    body = rewrite(doc['body'], data['instruction'], workspace['evidence'])
                    self.respond(store.save(data['document'], body, data['revision'], 'Local model revision; factual review required'))
                elif path == "/api/feedback":
                    if data.get("consent") is not True or set(data) != {"kind", "value", "consent"}:
                        raise ValueError("Explicit consent and only category/value accepted")
                    store.feedback(data["kind"], data["value"])
                    self.respond({"saved_locally": True, "transmitted": False})
                else:
                    self.respond({"error": "Not found"}, 404)
            except (ValueError, KeyError, TypeError, AttributeError) as e:
                self.respond({"error": str(e)}, 400)

    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"luna.europe review workspace: http://{host}", flush=True)
    httpd.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / ".private")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(args.data_dir.resolve(), args.port)
