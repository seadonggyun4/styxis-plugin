# Truthound operator environment (schema 2)

Only .env.template and this README belong in Git. Actual .env.local values,
research definitions, assignments and receipts are private. Static websites have
no runtime environment variables; these settings belong to the local operator.

    cp env-truthound/.env.template env-truthound/.env.local
    chmod 600 env-truthound/.env.local
    besties validate-environment env-truthound/.env.local
    besties validate-catalog /absolute/private/publication-catalog.json

Fill absolute paths for approved facts, private study, public output, the publication
catalog and approved layout locks, then select hosting teams. Authentication uses
the official CLI login store by default. Optional provider tokens can be injected
from a secret store. Tokens are never copied out of CLI storage or put in command
arguments, static files or public receipts.

OperatorEnvironment.load(path) loads only an explicit file. Process variables
override file values. Unknown/duplicate file keys, unsupported versions, empty
required settings, shell interpolation and unsafe permissions fail closed. There
is no automatic dotenv search, shell sourcing or mutation of os.environ.

## Responsibility boundaries

- Persona system names, versions, members and permanent numbers belong to the
  external domain definition, parsed by PersonaSystem.
- NamingPolicy generates project names from product/purpose and a SiteIdentity.
  Baseline is a separate role, never a numbered member.
- DeploymentRegistry records actual URLs and provider bindings. It is not a URL
  template and does not claim a deployment is live; HTTP receipts establish that.
- BESTIES_CATALOG_PATH is only an operator path to that definition. The environment
  does not contain a persona count, number range, project prefix or URL formula.
- BESTIES_LAYOUT_LOCK_PATH identifies the existing approved UI/output locks.
  Routine publication must verify these; it must not refresh them.

The public engine accepts different external systems and products. Private system
names and member mappings must not be copied into this folder or public examples.
Only DeploymentBinding.public_site() supplies public site configuration to renderers.

## Explicit migration from environment schema 1

Back up the existing environment outside Git. Move the system/member mapping into
the private catalog, record every existing deployed URL in its registry and verify
coverage before changing the operator. Set schema 2, add BESTIES_CATALOG_PATH,
and remove project-prefix, baseline-URL, persona-URL-template and FIRST/LAST keys.
Legacy domain keys are rejected in both files and process overrides: they must not
silently affect or conflict with the new catalog. Do not regenerate URLs or renumber
existing members during this migration. Existing renderer inputs, reviewed plan
hashes and layout locks remain unchanged.

Product-specific environment folder names are conventions, not engine dependencies.
environment.runner(provider) supplies only the selected provider credential.
All environment files, including templates, are rejected from upload bundles.
Hosting remains static-only; Git pushes do not deploy sites.
