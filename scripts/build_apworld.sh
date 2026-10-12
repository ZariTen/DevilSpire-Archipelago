#!/usr/bin/env bash
# Build build/devilspire.apworld (zip with a top-level "devilspire/" folder) including the bsdiff4 game patch.
#   scripts/build_apworld.sh [pristine data.win] [patched data.win]
# Defaults: game-copy/data.win and game-copy/data_patched.win (make the latter with patch/apply_patch.sh).
# The patch is built by scripts/make_patch.py with $PYTHON (needs bsdiff4; default: python3 if it has it, else
# `nix shell` with python3 + bsdiff4). Note: for official packaging use the Launcher's "Build APWorlds".
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
py="${PYTHON:-python3}"
if command -v "$py" >/dev/null && "$py" -c 'import bsdiff4' 2>/dev/null; then
  "$py" "$root/scripts/make_patch.py" "$@"
else
  nix shell --impure --expr 'with import <nixpkgs> {}; python3.withPackages (p: [ p.bsdiff4 ])' \
    -c python3 "$root/scripts/make_patch.py" "$@"
fi
mkdir -p "$root/build"
out="$root/build/devilspire.apworld"
rm -f "$out"
cd "$root/worlds-src"
z() { if command -v zip >/dev/null; then zip "$@"; else nix shell nixpkgs#zip -c zip "$@"; fi; }
z -r -q "$out" devilspire -x '*/__pycache__/*' '*.pyc'
z -sf "$out" | grep -q 'devilspire/data/devilspire.bsdiff4' || { echo "patch missing from apworld" >&2; exit 1; }
echo "built $out"
