#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="$repo_root/.claude-plugin/marketplace.json"

command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
command -v claude >/dev/null || { echo "claude is required" >&2; exit 1; }

test -f "$manifest"
test -f "$repo_root/README.md"
test -f "$repo_root/docs/security.md"

claude plugin validate "$repo_root"

source_url="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"][0]["source"]["url"])' "$manifest")"
source_sha="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"][0]["source"]["sha"])' "$manifest")"
source_path="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"][0]["source"]["path"])' "$manifest")"

git ls-remote "$source_url" | grep -q "$source_sha"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
git clone --filter=blob:none --no-checkout "$source_url" "$tmp_dir/source"
git -C "$tmp_dir/source" checkout --detach "$source_sha"

test -f "$tmp_dir/source/$source_path/.mcp.json"
test -f "$tmp_dir/source/$source_path/skills/truthound-setup/SKILL.md"
mkdir -p "$tmp_dir/source/$source_path/.claude-plugin"
cp "$repo_root/tests/fixtures/truthound-plugin.json" \
  "$tmp_dir/source/$source_path/.claude-plugin/plugin.json"
claude plugin validate "$tmp_dir/source/$source_path"

echo "styxis-plugin marketplace validation passed"
