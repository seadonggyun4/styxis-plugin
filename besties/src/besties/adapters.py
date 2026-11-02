"""Explicit page adapters: core never discovers arbitrary local files."""
from dataclasses import dataclass
from typing import Protocol
from urllib.request import Request, build_opener, HTTPRedirectHandler


@dataclass(frozen=True)
class Page:
    url: str
    status: int
    headers: dict
    html: str
    source: str


class Reader(Protocol):
    def read(self, url: str) -> Page: ...


class SnapshotReader:
    """Caller explicitly binds public URLs to local snapshots."""
    def __init__(self, pages: dict[str, Page]):
        self.pages = pages

    def read(self, url):
        return self.pages[url]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class HTTPReader:
    """Opt-in GETs to exact configured URLs, with redirects disabled."""
    def __init__(self, allowed_urls, timeout=15, max_bytes=2_000_000):
        self.allowed = frozenset(allowed_urls)
        self.timeout, self.max_bytes = timeout, max_bytes

    def read(self, url):
        if url not in self.allowed:
            raise ValueError("URL outside configured targets")
        request = Request(url, headers={"User-Agent": "Besties/0.1 (public-page-audit)"})
        with build_opener(NoRedirect).open(request, timeout=self.timeout) as response:
            raw = response.read(self.max_bytes + 1)
            if len(raw) > self.max_bytes:
                raise ValueError("Response exceeds size limit")
            headers = {k.lower(): v for k, v in response.headers.items()}
            if "text/html" not in headers.get("content-type", ""):
                raise ValueError("Expected HTML")
            return Page(url, response.status, headers,
                        raw.decode(response.headers.get_content_charset() or "utf-8"), "live_http")
