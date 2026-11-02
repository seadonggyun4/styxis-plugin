"""Validate public inputs before generating any artifacts."""
from dataclasses import dataclass
from urllib.parse import urlsplit, parse_qsl
import re


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def public_url(value):
    require(isinstance(value, str), "URL must be a string")
    parsed = urlsplit(value)
    require(parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username
            and not parsed.password and not parsed.query and not parsed.fragment,
            "Expected a credential-free HTTPS URL without query or fragment")
    return value


def public_reference_url(value):
    """Allow public document selectors without relaxing deployment-origin URLs."""
    require(isinstance(value, str) and not any(c.isspace() or ord(c) < 32 for c in value), 'Invalid reference URL')
    parsed = urlsplit(value)
    public_url(parsed._replace(query='').geturl())
    selectors = parse_qsl(parsed.query, keep_blank_values=True, strict_parsing=True)
    require(all(k in ('id', 'contentsid', 'lang', 'language') and
                re.fullmatch(r'[A-Za-z0-9_-]{1,120}', v) for k, v in selectors), 'Unsupported public document selector')
    require(len({k for k, _ in selectors}) == len(selectors), 'Duplicate document selector')
    return value


def fields(value, required):
    require(isinstance(value, dict) and set(value) == set(required),
            "Unexpected or missing fields: " + ", ".join(required))


def text(value):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= 4000,
            "Expected nonempty bounded text")
    return value


def identifier(value):
    require(isinstance(value, str) and bool(re.fullmatch(r"[a-z][a-z0-9-]{0,63}", value)),
            "Invalid identifier")
    return value


@dataclass(frozen=True)
class Project:
    data: dict

    @classmethod
    def parse(cls, data):
        fields(data, ("schema_version", "product", "evidence", "claims", "targets", "queries", "policy"))
        require(type(data["schema_version"]) is int and data["schema_version"] == 1, "Unsupported schema version")
        product = data["product"]
        fields(product, ("id", "name", "category", "version"))
        identifier(product["id"])
        for key in ("name", "category", "version"):
            text(product[key])
        for collection in ("evidence", "claims", "targets", "queries"):
            require(isinstance(data[collection], list) and bool(data[collection]), "Empty " + collection)
            ids = [identifier(item.get("id")) for item in data[collection] if isinstance(item, dict)]
            require(len(ids) == len(data[collection]) == len(set(ids)), "Invalid/duplicate " + collection)
        evidence_ids = set()
        for item in data["evidence"]:
            fields(item, ("id", "url", "label", "visibility"))
            public_url(item["url"])
            text(item["label"])
            require(item["visibility"] == "public", "Only explicitly public evidence is accepted")
            evidence_ids.add(item["id"])
        claim_ids = set()
        for item in data["claims"]:
            fields(item, ("id", "statement", "evidence", "kind"))
            text(item["statement"])
            require(item["kind"] in ("capability", "limitation", "identity"), "Invalid claim kind")
            require(isinstance(item["evidence"], list) and bool(item["evidence"])
                    and all(isinstance(e, str) and e in evidence_ids for e in item["evidence"]), "Unbound claim")
            claim_ids.add(item["id"])
        for item in data["targets"]:
            fields(item, ("id", "url", "locale", "required_terms", "required_links"))
            public_url(item["url"])
            text(item["locale"])
            require(isinstance(item["required_terms"], list) and bool(item["required_terms"]), "Missing required terms")
            for term in item["required_terms"]:
                text(term)
            require(isinstance(item["required_links"], list), "Invalid links")
            for link in item["required_links"]:
                public_url(link)
        for item in data["queries"]:
            fields(item, ("id", "text", "split", "intent", "claims"))
            text(item["text"])
            text(item["intent"])
            require(item["split"] in ("development", "holdout"), "Invalid query split")
            require(product["name"].casefold() not in item["text"].casefold(), "Queries must be unbranded")
            require(isinstance(item["claims"], list) and bool(item["claims"])
                    and all(isinstance(c, str) and c in claim_ids for c in item["claims"]), "Unbound query")
        require({q["split"] for q in data["queries"]} == {"development", "holdout"}, "Both query splits required")
        fields(data["policy"], ("mode", "preserve", "publication"))
        require(data["policy"]["mode"] == "propose", "This release only supports proposal mode")
        require(data["policy"]["publication"] == "public-input-only", "Public inputs required")
        require(data["policy"]["preserve"] == ["github_about", "readme_banner"], "Preservation policy required")
        return cls(data)
