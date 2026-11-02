# Discovery metadata

## Canonical identity

> Truthound is a local-first data quality and validation tool for AI agents. It
> validates, profiles, and scans approved local CSV and Parquet datasets without
> uploading raw values.

Primary intent:

- data quality
- data validation

Related intents:

- CSV and Parquet validation
- data profiling
- null and duplicate detection
- schema consistency
- PII and sensitive-data detection
- RAG source quality
- evaluation dataset validation
- local, private, and offline data inspection

Negative boundaries:

- not a dataset editor;
- not a cloud uploader;
- not a general database migration tool;
- not a legal compliance determination;
- not a hosted MCP service.

## Discovery layers

1. Claude Marketplace makes the plugin discoverable to users who add this
   catalog.
2. Official MCP Registry metadata supports discovery across MCP clients.
3. Product pages and technical evidence support web and generative-engine
   discovery.
4. MCP tool names, descriptions, and schemas drive post-install tool selection.

No single channel guarantees discovery by every agent. Release evaluation should
measure Registry Recall@10, Plugin Recall@5, Tool Hit@3, false-selection rate,
install success, and first-call success using positive and negative queries.
