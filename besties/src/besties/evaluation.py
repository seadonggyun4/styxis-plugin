"""Import structured observations without equating URL retrieval with recommendation."""
from .model import fields, require, public_url, text
from .planner import fingerprint


def evaluate(project, observations):
    require(isinstance(observations, list), "Observations must be a list")
    queries = {q["id"]: q for q in project.data["queries"]}
    seen, rows = set(), []
    for item in observations:
        fields(item, ("query_id", "provider", "surface", "observed_at", "status", "urls", "brand_mentioned", "brand_prompted", "fresh_session"))
        require(item["query_id"] in queries, "Unknown query")
        text(item["provider"])
        text(item["observed_at"])
        require(item["surface"] in ("search_results", "ai_answer"), "Invalid observation surface")
        key = (item["query_id"], item["provider"], item["surface"], item["observed_at"])
        require(key not in seen, "Duplicate observation")
        seen.add(key)
        require(item["status"] in ("completed", "unavailable"), "Invalid observation status")
        require(isinstance(item["urls"], list), "Invalid URLs")
        for url in item["urls"]:
            public_url(url)
        require(all(type(item[k]) is bool for k in ("brand_prompted", "fresh_session")), "Invalid session flags")
        require(item["brand_mentioned"] is None or type(item["brand_mentioned"]) is bool, "Invalid mention")
        if item["status"] == "unavailable":
            require(not item["urls"] and item["brand_mentioned"] is None, "Unavailable is not a negative result")
        organic = item["status"] == "completed" and not item["brand_prompted"] and item["fresh_session"]
        target_urls = {t["url"].rstrip("/") for t in project.data["targets"]}
        rows.append({**item, "split": queries[item["query_id"]]["split"], "eligible_unbranded_observation": organic,
                     "configured_target_returned": any(u.rstrip("/") in target_urls for u in item["urls"]) if item["status"] == "completed" else None})
    return {"schema_version": 1, "input_sha256": fingerprint(project), "observations": rows,
            "scope": "Imported operator observations; provenance and citation correctness require external verification. No causal improvement estimate.",
            "unmeasured_queries": sorted(set(queries) - {r["query_id"] for r in rows if r["eligible_unbranded_observation"]})}
