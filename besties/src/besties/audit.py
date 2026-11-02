"""Observable page checks, explicitly separate from indexing and recommendation."""
from html.parser import HTMLParser
from urllib.parse import urljoin
import hashlib
import re
from .planner import fingerprint


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.exclusions = []
        self.regions = {key: {"text": [], "links": []} for key in ("body", "main", "article")}
        self.depth = {key: 0 for key in self.regions}
        self.seen = set()
        self.stack = []
        self.in_body = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "body":
            self.in_body = True
        if tag in self.depth:
            self.depth[tag] += 1
            self.seen.add(tag)
        if tag in ("script", "style", "template"):
            self.stack.append(tag)
        if tag == "meta" and attrs.get("name", "").lower() in ("robots", "googlebot", "bingbot"):
            if re.search(r"\b(noindex|none)\b", attrs.get("content", ""), re.I):
                self.exclusions.append("meta_noindex")
        if self.in_body and not self.stack and tag == "a" and "href" in attrs:
            for region in self.regions:
                if self.depth[region]:
                    self.regions[region]["links"].append(attrs["href"])

    def handle_endtag(self, tag):
        if tag in self.depth:
            self.depth[tag] = max(0, self.depth[tag] - 1)
        if tag == "body":
            self.in_body = False
        if self.stack and tag == self.stack[-1]:
            self.stack.pop()

    def handle_data(self, data):
        if self.in_body and not self.stack:
            for region in self.regions:
                if self.depth[region]:
                    self.regions[region]["text"].append(data)

    def content(self):
        for region in ("article", "main", "body"):
            if region in self.seen:
                return region, self.regions[region]
        return "body", self.regions["body"]


def audit(project, reader):
    results = []
    for target in project.data["targets"]:
        row = {"target_id": target["id"], "url": target["url"]}
        try:
            page = reader.read(target["url"])
            document = Document()
            document.feed(page.html)
            region, content = document.content()
            body = " ".join(" ".join(content["text"]).split()).casefold()
            links = {urljoin(page.url, link).rstrip("/") for link in content["links"]}
            exclusions = list(document.exclusions)
            headers = {k.lower(): v for k, v in page.headers.items()}
            if re.search(r"\b(noindex|none)\b", headers.get("x-robots-tag", ""), re.I):
                exclusions.append("header_noindex")
            missing = [t for t in target["required_terms"] if " ".join(t.split()).casefold() not in body]
            missing_links = [u for u in target["required_links"] if u.rstrip("/") not in links]
            passed = page.status == 200 and page.url == target["url"] and bool(body.strip()) and not (exclusions or missing or missing_links)
            row.update(status="passed" if passed else "failed", source=page.source, content_region=region,
                       http_status=page.status, exclusions=exclusions, missing_terms=missing,
                       missing_links=missing_links, html_sha256=hashlib.sha256(page.html.encode()).hexdigest())
        except Exception as exc:
            # Paths, response bodies and credentials never become public error details.
            row.update(status="unmeasured", error_type=type(exc).__name__)
        results.append(row)
    return {"schema_version": 1, "input_sha256": fingerprint(project), "pages": results,
            "passed": all(r["status"] == "passed" for r in results),
            "scope": "HTML article/main/body text and links (in that preference order), HTTP status and noindex only; not a rendered-browser, robots.txt or factual-accuracy audit",
            "indexing": "unmeasured", "organic_discovery": "unmeasured"}
