#!/usr/bin/env bash
# Publish a GitHub release from this machine (only the local build has the patch data).
#   PYTHON=/tmp/ap-venv/bin/python scripts/release.sh 0.1.0
# Needs: clean main pushed to origin, gh logged in, a "## v<version>" section in CHANGELOG.md.
# Builds the apworld, checks the version/label, makes a signed tag, pushes it and creates the release
# (pre-release for 0.x) with devilspire.apworld and DevilSpire.yaml attached.
set -euo pipefail
v="${1:?usage: release.sh <version, e.g. 0.1.0>}"; tag="v$v"
py="${PYTHON:-python3}"
root="$(cd "$(dirname "$0")/.." && pwd)"; cd "$root"
gh="gh"; command -v gh >/dev/null || gh="nix shell nixpkgs#gh -c gh"
$gh auth status >/dev/null || { echo "gh is not logged in (run: gh auth login)" >&2; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "working tree not clean" >&2; exit 1; }
git fetch -q origin main
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || { echo "HEAD is not origin/main; push first" >&2; exit 1; }
wv="$("$py" -c 'import json;print(json.load(open("worlds-src/devilspire/archipelago.json"))["world_version"])')"
[ "$wv" = "$v" ] || { echo "world_version is $wv, not $v" >&2; exit 1; }
notes="$(mktemp)"; trap 'rm -f "$notes"' EXIT
awk -v h="## $tag" '$0==h{f=1;next} /^## /{f=0} f' CHANGELOG.md > "$notes"
[ -s "$notes" ] || { echo "no '## $tag' section in CHANGELOG.md" >&2; exit 1; }
scripts/build_apworld.sh
label="$("$py" -c 'import json,zipfile;print(json.loads(zipfile.ZipFile("build/devilspire.apworld").read("devilspire/data/patch.json"))["mod_label"])')"
case "$label" in "Archipelago $tag "*) ;; *) echo "patch label '$label' does not match $tag" >&2; exit 1;; esac
git rev-parse -q --verify "refs/tags/$tag" >/dev/null || git tag -s "$tag" -m "Devil Spire Archipelago $tag"
git push origin "$tag"
pre=""; case "$v" in 0.*) pre="--prerelease";; esac
cp examples/DevilSpire.yaml build/DevilSpire.yaml
$gh release create "$tag" --verify-tag $pre --title "$tag" --notes-file "$notes" \
  build/devilspire.apworld build/DevilSpire.yaml
