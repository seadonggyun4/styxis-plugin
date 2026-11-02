# Agent Discovery Optimization: evidence review

Reviewed 2026-11-02 (Asia/Seoul). This is an engineering synthesis, not a systematic
review or a claim that an agent vendor implements any particular research method.
Primary papers, proceedings and official contracts were opened; blogs about those
papers were not used as evidence. Paper scores below belong to their original
experiments and are **not Truthound results**. Preprint status means that a
peer-reviewed publication was not established by this audit, not that none exists.

## Literature ledger

| ID / primary source | Review / venue | Subject and benchmark scale | Finding | Truthound application | Non-application / limits |
| --- | --- | --- | --- | --- | --- |
| R1 [Aggarwal et al., GEO](https://arxiv.org/abs/2311.09735), [KDD proceedings](https://doi.org/10.1145/3637528.3671900) | Peer-reviewed, KDD 2024 | GEO-bench: 10,000 queries across domains; a simulated generative engine and deployed-engine experiment | Evidence/citations/statistics can improve citation-weighted visibility; keyword stuffing was ineffective; gains vary by domain | Publish bounded, dated, reproducible claims with direct sources | Reported up-to-40% is neither an expected Truthound lift nor a tool-retrieval result; content already reaching a retrieval pool is a different problem from getting indexed |
| R2 [Chen et al., How to Dominate AI Search](https://arxiv.org/html/2509.08919v1) | Preprint, arXiv 2025 | Regional experiment: 1,000 prompts, 10 categories, US/Canada; separate language/paraphrase studies and four named search engines | Source mix and language sensitivity vary; the study observes earned-media preference | Track owned/earned sources and EN/KO citations separately | Consumer ranking prompts, automated source labels, temporal snapshots and engine-specific methods do not establish causal authority for all products; no Korean lift is established |
| R3 [Manning, Raghavan, Schütze, Introduction to IR](https://nlp.stanford.edu/IR-book/) | Academic textbook, Cambridge UP 2008; not a benchmark paper | Classical indexing, query expansion, ranking and evaluation; no single benchmark size | Relevance judgments, ranked metrics and precision/recall tradeoffs are necessary | Implement explicit qrels, stage denominators, ranking metrics and held-out slices | Classical lexical retrieval is a baseline, not a model of a proprietary agent |
| R4 [Karpukhin et al., DPR](https://aclanthology.org/2020.emnlp-main.550/) | Peer-reviewed, EMNLP 2020 | Five open-domain QA datasets; Wikipedia passage retrieval | Dense dual encoders can retrieve semantic matches missed by term overlap | Plan a separately identified dense/hybrid experiment when a local embedding runtime is available | QA passage results do not transfer numerically to MCP metadata or Korean tools |
| R5 [Thakur et al., BEIR](https://arxiv.org/abs/2104.08663) | Peer-reviewed, NeurIPS 2021 Datasets and Benchmarks (paper record) | 18 datasets, 10 retrieval systems in the cited version | BM25 is robust; reranking/late interaction trade quality against cost; generalization differs by domain | Keep a sparse baseline, multiple intents and difficult distractors | No universal dense-over-sparse advantage; local fixture scores are not ecosystem recall |
| R6 [Qin et al., ToolLLM / ToolBench](https://arxiv.org/abs/2307.16789), [ICLR paper](https://openreview.net/attachment?id=dHng2O0Jjr&name=pdf) | Peer-reviewed, ICLR 2024 | 16,464 REST APIs, 49 RapidAPI categories; synthetic instructions and annotated solution paths | Neural retrieval plus planning enables tool use at scale | Record retrieval separately from successful tool execution | Synthetic instructions, changing remote APIs and evaluator assumptions limit transfer; not local stdio installation research |
| R7 [Patil et al., Gorilla / APIBench](https://proceedings.nips.cc/paper_files/paper/2024/hash/e4c61f578ff07830f5c37378dd3ecb0d-Abstract-Conference.html), [paper](https://proceedings.nips.cc/paper_files/paper/2024/file/e4c61f578ff07830f5c37378dd3ecb0d-Paper-Conference.pdf) | Peer-reviewed, NeurIPS 2024 | Approximately 1,600 ML APIs from three hubs; AST-based API-call evaluation | Retrieval-aware training helps adapt to updated API documents and reduce hallucinated calls | Preserve versioned input schemas and evaluate argument correctness | API syntax correctness does not prove permissions, installation or safe execution; trained-model gains cannot be promised from prose edits |
| R8 [Du et al., AnyTool](https://proceedings.mlr.press/v235/du24h.html), [authors' implementation](https://github.com/dyabel/AnyTool) | Peer-reviewed, ICML 2024 (PMLR 235) | Over 16,000 APIs; ToolBench and additional AnyToolBench | Hierarchical candidate discovery, solver and reflection; identifies inflated pass-rate evaluation | Separate candidate coverage from actual task completion; permit abstention | Tool hierarchy costs latency and may not exist in arbitrary catalogs; no need to add a hierarchy server for three tools |
| R9 [Huang et al., MetaTool](https://proceedings.iclr.cc/paper_files/paper/2024/hash/bc12914d66b41b6bfc2d3a5decdb498b-Abstract-Conference.html), [dataset](https://github.com/HowieHwong/MetaTool) | Peer-reviewed, ICLR 2024; later arXiv revisions distinguished | Authors report 21,127 checked ToolE queries: 20,630 single-tool, 497 multi-tool; eight evaluated LLMs | Tool-use awareness differs from choosing among similar tools; description rewriting depends on downstream model | Add no-tool negatives, similar choices, multi-intent labels and rewrite A/B checks | Description gains are model-dependent; an arbitrary longer description is not automatically better |
| R10 [Chen et al., Re-Invoke](https://aclanthology.org/2024.findings-emnlp.270/), [paper](https://aclanthology.org/2024.findings-emnlp.270.pdf) | Peer-reviewed, Findings of EMNLP 2024 | ToolBench I1/I2/I3 and ToolE single/multi; 16k+ API retrieval, ten generated queries per tool in the method | Intent extraction and document expansion improve nDCG; paper reports relative ToolE nDCG@5 gains of 20%/39% | Add task examples, distinguish multi-intent coverage and keep query expansion an explicit future ablation | Our BM25 runner does not implement Re-Invoke, use its embeddings or reproduce its scores; expansion can introduce drift |
| R11 [Fei et al., MCP-Zero](https://arxiv.org/html/2506.01056v4) | Preprint, arXiv 2025 | 308 MCP servers, 2,797 tools; APIBank and needle tests | Active requests, server→tool semantic routing and iterative extension reduce context load | Separate server-level and tool-level contracts; allow capability-gap-driven discovery | It supplies an indexed catalog and custom runtime; Registry publication does not cause this behavior in all hosts |
| R12 [Gan and Sun, RAG-MCP](https://arxiv.org/html/2505.03275v1) | Preprint, arXiv 2025 | WebSearch tasks; 20 trials; says >4,400 catalog servers and stress N up to 11,100 | Reports 43.13% vs 13.62% selection and >50% prompt reduction | Retrieval before schema loading is a testable architectural hypothesis | Narrow task set, model-as-judge and unclear reconciliation of catalog size versus largest N limit confidence; no cross-client or Truthound guarantee |

## Official contracts, separated from research

| ID | Source | Contract or observation used |
| --- | --- | --- |
| O1 | [Claude marketplace distribution](https://code.claude.com/docs/en/plugin-marketplaces) | Users add catalogs explicitly; `strict` selects component authority. It is not sandbox strictness. Git subdirectory sources support immutable SHA pins. `${CLAUDE_PLUGIN_ROOT}` anchors launcher paths. Installed CLI 2.1.196 behavior is checked independently of newer web docs. |
| O2 | [MCP Registry ecosystem](https://modelcontextprotocol.io/registry/about), [package types](https://modelcontextprotocol.io/registry/package-types) | Registry hosts install metadata pointing to packages, not the code; downstream aggregators curate and synchronize it. A local stdio package can be listed without a remote MCP endpoint. |
| O3 | [MCP tools specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) | `tools/list` exposes names, descriptions, schemas and annotations after connection. Clients decide interaction and loading; annotations are hints, not a permission enforcement system. |
| O4 | [Anthropic advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) | Deferred definitions, tool search and examples are client/API features; discoverable names/descriptions and parameter examples serve different roles. The published engineering experiments are not peer-reviewed cross-vendor evidence. |
| O5 | [OpenAI tool search](https://developers.openai.com/api/docs/guides/tools-tool-search) | Searchable server/namespace summaries guide deferred loading. Responses hosted search uses declared tools; client-executed search uses a supplied lookup. This is not universal internet search for absent local servers. |
| O6 | [GitHub topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics), [repository search](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories), [languages](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-repository-languages) | Topics and repository fields aid discovery; code/repository search differ. Language statistics are computed by Linguist. These are read-only audit surfaces here: the user prohibits About changes without a separate explicit request. |
| O7 | [Google localized pages](https://developers.google.com/search/docs/specialty/international/localized-versions), [structured data guidance](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data) | Use reciprocal locale URLs and supported semantic markup matching visible content; neither guarantees indexing, ranking or AI citation. |
| O8 | [Registry versioning](https://modelcontextprotocol.io/registry/versioning), [authentication](https://modelcontextprotocol.io/registry/authentication) | Published versions are immutable; new metadata needs a new version and namespace authorization. GitHub push is not publication. Registry-only updates can use distinct prerelease versions while package pins remain fixed. |

`llms.txt` is supplied as a useful navigational text artifact. No reviewed protocol
or vendor contract here establishes that it increases ranking or is consumed by
all agents. Similarly JSON-LD improves explicit entity representation without
establishing an algorithmic ranking benefit.

## Answers to the twelve design questions

1. **Absent-server discovery:** web/search tools, GitHub, package registries,
   explicitly added catalogs, a host's connected registry/aggregator or an
   operator's instructions can introduce a candidate. Each requires a client
   capability and an accessible index. No repository can force an unconnected
   host to search it. (O1–O5; R11.)
2. **Unadded custom marketplaces:** there is no general contract that Claude
   searches all public custom catalogs. A browsing-capable agent can find the
   repository as a web document; adding/installing it is a separate action. The
   owned catalog must have independent web/GitHub entry points. (O1.)
3. **Registry role:** normalized identity, package/version/transport/arguments and
   namespace provenance make server metadata consumable by aggregators. Catalog
   ingestion, filtering, sync latency and client search remain external. (O2.)
4. **Server versus tool descriptions:** summaries identify a relevant capability
   group before detailed schemas are loaded. Individual tools then determine
   whether `check_file`, `profile_file` or `scan_pii` fits, and which arguments are
   valid. An excellent tool cannot repair a missed upstream candidate. (O3–O5.)
5. **Adjacent intents:** anchor one identity in data quality/data validation, then
   provide task→input→supported check→bounded result examples. RAG/eval only
   extends the context of supported tabular preparation, not the capability into
   semantic evaluation. Schema observation is separated from custom validation.
6. **Broad versus narrow:** broad vocabulary can improve candidate recall while
   retrieving irrelevant tasks; sparse matching may even match a negated word.
   Narrow descriptions lose paraphrases. Measure both relevance and negative
   exposure; tune on development cases and report the fixed split separately. The current holdout was inspected during iteration and is diagnostic, not a blind estimate. (R3/R5.)
7. **Examples and negative boundaries:** examples can clarify tool use and argument
   construction; limits enable abstention. They are hypotheses for each host,
   not proven boosts. Negative wording can *increase* lexical matching, so actual
   selection needs its own observed metric. (R9/R10/O4.)
8. **Framework ambiguity:** describe the Local surface precisely and label explicit
   Great Expectations suite, Pandera DataFrameSchema and Soda SQL requests as
   other-framework tasks. Do not claim substitutes are inferior or share API
   compatibility. Synthetic competitor sketches are not vendor evaluations.
9. **Korean and English:** maintain localized canonical pages with the same facts,
   reciprocal hreflang, concise Korean intent wording and balanced query slices.
   Translation-equivalent cases stay in the same evaluation split. Sparse Korean
   bigrams are an explicit baseline; dense cross-language benefit is unmeasured.
10. **Failed conversion:** record attempted install, startup, discovery, first
    approved call and correct denial as separate events, versioned to the exact
    artifact. A transport success with quality failures is not clean data. A
    missing observation is pending; a failed attempted execution stays failed.
11. **Unified funnel:** record web mention/citation/correct identity, Registry
    candidate, plugin candidate, selected tool, consent and completed task. Do
    not multiply independently sampled stage rates into an invented conversion
    rate. Linked real runs can measure conditional rates and end-to-end success.
12. **Realistic success:** require reproducible installation and boundary checks,
    improve ranked coverage on fixed representative cases while watching false
    selection, and accumulate client/model-specific observed task completion.
    Universal discovery, endorsement, ranking and a compliance guarantee are not
    success criteria this repository can promise.

## Retrieval and evaluation design

Sparse retrieval scores observed words; dense retrieval compares learned semantic
representations; hybrid retrieval combines their ranked evidence, for example
with reciprocal rank fusion, before optional reranking. This implementation
ships only a deterministic BM25 baseline. It does not introduce a hosted index,
central RAG service, embedding API or model expense. A future local dense/hybrid
ablation must record the embedding model, tokenizer, weights, index snapshot,
query expansion and reranker, use identical qrels/candidate sets, and retain the
sparse result. An oracle-candidate selection experiment isolates retrieval loss
from final selection loss. A raw-query retrieval experiment and a plan-then-retrieve
experiment should use the same inputs and budget; planning can disambiguate
multi-intent requests but can also rewrite away constraints. No reviewed source
establishes a universal retrieve-first or plan-first winner for Truthound.

Hierarchy is data quality → local tabular inputs → checks/profile/PII, not a list
of unrelated product brands. Chunk each use case around its input, intended tool,
result and negative boundary. Keep identity, version and permission context in
that chunk so it remains meaningful in an excerpt. Progressive discovery belongs
to hosts that support it, not an extra MCP gateway bolted onto three tools.

Recall@k = retrieved relevant / all relevant; Hit@k = at least one relevant
candidate; precision@k = relevant retrieved / retrieved positions. MRR uses the
first relevant rank, with missing relevant items scoring zero. nDCG uses graded
`(2^gain - 1) / log2(rank + 1)` normalized by ideal ordering. Negative-only cases
have no recall/nDCG denominator; evaluate abstention and false target selection.
Multi-intent cases can have Hit=1 and Recall<1. Ranked candidate exposure is not
an observed selection. The runner records all these distinctions, coverage,
failures, split/language/category slices and hashes.

Owned evidence should be correct and reproducible before seeking independent
review. Earned citations may add independent verification, but self-authored
aggregator mirrors are not independent validation. Do not manufacture quotations,
statistics, reviews or endorsements to imitate a GEO treatment.
