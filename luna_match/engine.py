"""Deterministic evidence rubric. No embeddings, inferred personality or hiring probability."""
import math
import time

VERSION = "evidence-rubric-0.1"
LEVELS = {"supported": 1.0, "partial": 0.5, "gap": 0.0, "unknown": 0.0}


def match(payload):
    start = time.perf_counter()
    evidence = payload.get("evidence", [])
    requirements = payload.get("requirements", [])
    if not isinstance(evidence, list) or not isinstance(requirements, list) or not 1 <= len(requirements) <= 100:
        raise ValueError("Supply 1–100 requirements and an evidence list")
    ids = [e.get("id") for e in evidence]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("Evidence IDs must be unique nonempty strings")
    sources = {e["id"]: e for e in evidence}
    rows, total, points, unknown, observed = [], 0., 0., 0., 0.
    hard_gaps, hard_unknown = [], []
    for r in requirements:
        label = r.get("label")
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Every requirement needs a label")
        w = r.get("weight", 1)
        if isinstance(w, bool) or not isinstance(w, (int, float)) or not math.isfinite(w) or not 0 < w <= 100:
            raise ValueError("Weights must be finite and in (0,100]")
        level = r.get("assessment", "unknown")
        if level not in LEVELS:
            raise ValueError("Invalid assessment")
        refs = r.get("evidence_ids", [])
        if not isinstance(refs, list) or any(not isinstance(i, str) or i not in sources for i in refs):
            raise ValueError("Unknown evidence reference")
        if level in ("supported", "partial") and (not refs or any(not sources[i].get("source") or not sources[i].get("text") for i in refs)):
            raise ValueError("Supported assessments require source-backed evidence")
        if r.get("hard") and level == "gap":
            hard_gaps.append(label)
        elif r.get("hard") and level != "supported":
            hard_unknown.append(label)
        total += w
        points += w * LEVELS[level]
        unknown += w if level == "unknown" else 0
        observed += w if level != "unknown" else 0
        rows.append({**r, "assessment": level, "contribution": w * LEVELS[level]})
    return {"version": VERSION, "score": round(100 * points / total, 1),
            "coverage": round(100 * observed / total, 1),
            "unknown_upper_bound": round(100 * (points + unknown) / total, 1),
            "eligibility": "blocked" if hard_gaps else "unresolved" if hard_unknown else "review_required",
            "hard_gaps": hard_gaps, "hard_unknown": hard_unknown,
            "requirements": rows, "runtime_ms": round((time.perf_counter() - start) * 1000, 3),
            "meaning": "Human-assessed evidence rubric; not hiring probability or validated accuracy."}
