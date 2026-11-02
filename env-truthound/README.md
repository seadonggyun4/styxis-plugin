# Truthound operator environment

Only `.env.template` and this README belong in Git. Actual `.env.local` values,
research inputs, assignments and receipts are private. The static website has no
runtime environment variables; these settings belong to the local publishing process.

```sh
cp env-truthound/.env.template env-truthound/.env.local
chmod 600 env-truthound/.env.local
```

Fill absolute paths for the approved facts, private study directory and public-output
directory; select the two hosting teams and project prefix. Never put the private
study directory itself in an upload command. Product-specific folders contain
configuration only: the engine has no dependency on this folder name or product.

Load explicitly with `OperatorEnvironment.load(path)`. Existing process variables
override file values. Unknown file keys, duplicates, unsupported versions, empty
required values, shell interpolation and unsafe permissions fail closed. There is
no automatic `.env` search, shell sourcing or mutation of `os.environ`.

Use `besties validate-environment env-truthound/.env.local` for a value-free check.
The check verifies configuration structure, not account access or file existence.

Credentials are optional. Local publication uses the existing official CLI login
store unless a token is explicitly configured. Tokens are never copied out of CLI
storage. `environment.runner(provider)` passes only that provider's token to the
child process; no token appears in command arguments, static files or receipts.
For CI, inject credentials from the CI secret store rather than committing a file.
This does not enable Git-connected hosting: deployment still uploads static files.

No environment file, including this template, is accepted in a deployment bundle.

## Fixed public addresses and presentation layout

The environment contains actual baseline origins and a literal `{number}` URL rule
for each provider. `BESTIES_PERSONA_FIRST=1` and `BESTIES_PERSONA_LAST=16` bound the
current range. `site_url(provider, role, number)` resolves the exact origin; duplicate
origins, unknown placeholders and out-of-range numbers are rejected. Changing a
URL setting does not rename a hosted project: the operator must migrate and verify
it explicitly. Canonical URLs must be rebuilt from the same configured addresses.

`BESTIES_LAYOUT_LOCK_PATH` points to a private approved release-lock registry.
Each target lock freezes HTML structure and accessibility hooks, CSS hashes and
artifact names, while permitting editorial text and URL changes. Publication calls
`publish(..., layout_lock=approved_lock)` before contacting the provider. The current
baseline and presentation layouts are frozen separately; changing their design
requires an explicitly approved new lock. Do not regenerate locks during routine
publication. A layout lock complements exact release verification; it is not a
full visual regression or semantic accessibility certification.
