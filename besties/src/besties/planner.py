"""Deterministic proposals; evidence references are not independent fact checks."""
from html import escape
import hashlib
import json


def fingerprint(project):
    return hashlib.sha256(json.dumps(project.data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def plan(project):
    data = project.data
    return {
        "schema_version": 1, "input_sha256": fingerprint(project),
        "product_id": data["product"]["id"], "mode": "propose",
        "evidence_status": "references_validated_content_not_independently_verified",
        "targets": data["targets"],
        "sections": [{"query_id": q["id"], "question": q["text"], "claim_ids": q["claims"]}
                     for q in data["queries"] if q["split"] == "development"],
        "preserve": data["policy"]["preserve"],
        "indexing": "unmeasured", "organic_discovery": "unmeasured",
    }


def render(project):
    """Render an escaped draft from supplied claims, never invent features."""
    data = project.data
    claims = {c["id"]: c for c in data["claims"]}
    evidence = {e["id"]: e for e in data["evidence"]}
    lines = ["<!doctype html><html><head><meta charset='utf-8'>",
             "<meta name='robots' content='noindex'>",
             f"<title>{escape(data['product']['name'])} — review draft</title></head><body>",
             f"<h1>{escape(data['product']['name'])}</h1>",
             f"<p>{escape(data['product']['category'])}</p>",
             "<p>Review draft. Supplied evidence references require editorial verification before publication.</p>"]
    for section in plan(project)["sections"]:
        lines.append(f"<h2>{escape(section['question'])}</h2>")
        for cid in section["claim_ids"]:
            claim = claims[cid]
            lines.append(f"<p>{escape(claim['statement'])}</p>")
            for eid in claim["evidence"]:
                e = evidence[eid]
                lines.append(f'<a href="{escape(e["url"], quote=True)}">{escape(e["label"])}</a>')
    lines.append("</body></html>")
    return "\n".join(lines) + "\n"
