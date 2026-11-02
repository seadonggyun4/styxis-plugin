#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="$repo_root/.claude-plugin/marketplace.json"
command -v git >/dev/null || { echo 'git is required' >&2; exit 1; }
command -v claude >/dev/null || { echo 'claude is required' >&2; exit 1; }
python3 "$repo_root/scripts/validate_metadata.py"
claude plugin validate "$repo_root"
source_url="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"][0]["source"]["url"])' "$manifest")"
source_sha="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"][0]["source"]["sha"])' "$manifest")"
source_path="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"][0]["source"]["path"])' "$manifest")"
plugin_version="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"][0]["version"])' "$manifest")"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
# A SHA need not be a branch/tag tip. Fetch and verify the object itself.
git init --quiet "$tmp_dir/source"
git -C "$tmp_dir/source" remote add origin "$source_url"
git -C "$tmp_dir/source" fetch --quiet --depth=1 origin "$source_sha"
test "$(git -C "$tmp_dir/source" rev-parse FETCH_HEAD)" = "$source_sha"
git -C "$tmp_dir/source" checkout --quiet --detach FETCH_HEAD
plugin="$tmp_dir/source/$source_path"
test -f "$plugin/.mcp.json"
test -f "$plugin/.claude-plugin/plugin.json"
test -f "$plugin/skills/truthound-setup/SKILL.md"
python3 - "$plugin/.claude-plugin/plugin.json" "$plugin_version" <<'PY'
import json,sys
manifest=json.load(open(sys.argv[1]))
assert manifest['name']=='truthound' and manifest['version']==sys.argv[2]
args=manifest['mcpServers']['truthound']['args']
assert '--directory' in args and '${CLAUDE_PLUGIN_ROOT}' in args
PY
# Validate the actual remote package. Never inject a fixture manifest.
claude plugin validate "$plugin"
python3 -m unittest discover -s "$repo_root/tests" -v
python3 "$repo_root/scripts/evaluate.py" --variant installed --output "$tmp_dir/evaluation.json" >/dev/null
echo 'Pinned remote source, standalone Claude package and evaluation validation passed'
