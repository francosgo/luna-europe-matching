"""Private revision history. Approval applies only to a specific content hash."""
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


class Store:
    def __init__(self, path):
        self.path = str(path)
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS revisions(id INTEGER PRIMARY KEY, document TEXT NOT NULL,
              revision INTEGER NOT NULL, body TEXT NOT NULL, hash TEXT NOT NULL, status TEXT NOT NULL,
              note TEXT NOT NULL, created TEXT NOT NULL, UNIQUE(document, revision));
            CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY, kind TEXT NOT NULL, value INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY, document TEXT NOT NULL,
              revision INTEGER NOT NULL, instruction TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending');
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def seed(self, document, body):
        if self.latest(document) is None:
            self.save(document, body, 0, "Initial draft")

    def latest(self, document):
        with self.connect() as db:
            row = db.execute("SELECT * FROM revisions WHERE document=? ORDER BY revision DESC LIMIT 1", (document,)).fetchone()
            return dict(row) if row else None

    def save(self, document, body, expected, note=""):
        if not isinstance(body, str) or not body.strip() or len(body) > 100000:
            raise ValueError("Document must contain 1–100000 characters")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute("SELECT revision FROM revisions WHERE document=? ORDER BY revision DESC LIMIT 1", (document,)).fetchone()
            version = current[0] if current else 0
            if expected != version:
                raise ValueError("Revision conflict: reload before editing")
            db.execute("INSERT INTO revisions(document,revision,body,hash,status,note,created) VALUES(?,?,?,?,?,?,?)",
                       (document, version + 1, body, digest(body), "draft", note, datetime.now(timezone.utc).isoformat()))
            db.execute("UPDATE requests SET status='revised' WHERE document=? AND status='pending'", (document,))
        return self.latest(document)

    def approve(self, document, expected, content_hash):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM revisions WHERE document=? ORDER BY revision DESC LIMIT 1", (document,)).fetchone()
            if not row or row["revision"] != expected or row["hash"] != content_hash:
                raise ValueError("Approval rejected: content changed")
            if db.execute("SELECT 1 FROM requests WHERE document=? AND status='pending'", (document,)).fetchone():
                raise ValueError("Resolve the pending change request before approval")
            db.execute("UPDATE revisions SET status='approved' WHERE id=?", (row["id"],))
        return self.latest(document)

    def request(self, document, revision, instruction):
        if not isinstance(instruction, str) or not 1 <= len(instruction.strip()) <= 4000:
            raise ValueError("Enter a change request of 1–4000 characters")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT id,revision FROM revisions WHERE document=? ORDER BY revision DESC LIMIT 1", (document,)).fetchone()
            if not row or row['revision'] != revision:
                raise ValueError("Revision conflict")
            db.execute("INSERT INTO requests(document,revision,instruction) VALUES(?,?,?)", (document, revision, instruction))
            db.execute("UPDATE revisions SET status='changes_requested' WHERE id=?", (row['id'],))

    def requests(self):
        with self.connect() as db:
            return [dict(x) for x in db.execute("SELECT * FROM requests WHERE status='pending'")]

    def feedback(self, kind, value):
        if kind not in ("useful_match", "unsupported_claim", "unclear_explanation") or type(value) is not int or value not in (0, 1):
            raise ValueError("Feedback accepts only an allowlisted category and binary value")
        with self.connect() as db:
            db.execute("INSERT INTO feedback(kind,value) VALUES(?,?)", (kind, value))

    def aggregate(self):
        with self.connect() as db:
            return [dict(x) for x in db.execute("SELECT kind,COUNT(*) AS n,SUM(value) AS positive FROM feedback GROUP BY kind HAVING COUNT(*)>=10")]
