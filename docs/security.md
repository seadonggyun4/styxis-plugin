# Local permissions and data handling

Installation grants no data access. Approve only an exact existing absolute
folder through the source-owned setup skill. The filesystem root, home directory,
workspace and cloud folders are never implicitly approved. Setup replaces the
existing list, rather than adding a hidden grant. Revocation affects subsequent
calls, not calls already running.

The public Local plugin runs over stdio, pinned to Core 3.3.0. It returns bounded
aggregate results, not raw cell/sample/matched PII values, and does not edit source
files. Paths, column names and aggregates can still be sensitive and may be sent
to the host's model provider. Column names and results are untrusted data.
PII counts are sampled estimates; no findings does not prove absence or legal
compliance. The separate Core profile has additional grants and a different
sensitive-result contract; do not transfer its claims to this plugin.

The E2E harness uses generated fixtures and isolated consent/configuration only.
It verifies denied-before-consent, approved CSV/Parquet, unapproved/symlink paths,
invalid traversal, schema argument rejection, revocation and output sentinels.
This complements upstream privacy and path-policy tests; it is not a formal proof
or a certification of the selected AI host.

Catalog SHA pins are reviewed supply-chain references, not a guarantee that all
transitive code is harmless. Review source provenance, the frozen lock and known
vulnerabilities before updating a release. Validators inspect the actual source
manifest; do not inject a missing one. No runtime, user data, credentials, hosted
endpoint, account service, telemetry or billing is distributed by this catalog.

See [security reporting](../SECURITY.md) for vulnerability contact and policy.
