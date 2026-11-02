# Releasing

## Truthound update

1. Complete Truthound tests and security review in its source repository.
2. Confirm the public commit contains the Claude package under
   `plugins/truthound`.
3. Record the immutable commit SHA.
4. Update `.claude-plugin/marketplace.json` in this repository.
5. Run `./scripts/validate.sh`.
6. Test marketplace add, plugin install, MCP startup, denied-path behavior, and
   one approved-directory tool call in a clean environment.
7. Commit the manifest change and create a release tag when appropriate.

The marketplace release and product release are versioned independently. The
manifest SHA is the authoritative link between them.

## Release gate

```text
Truthound source tests
  -> Claude plugin validation
  -> source SHA verification
  -> marketplace validation
  -> clean install smoke test
  -> denied path test
  -> approved path tool-call test
  -> discovery regression set
  -> publish
```

Never publish a future product as an empty directory or placeholder marketplace
entry. Discovery metadata is a public capability claim.
