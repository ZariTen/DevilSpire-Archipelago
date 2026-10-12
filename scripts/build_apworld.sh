#!/usr/bin/env bash
# Zip worlds-src/devilspire into build/devilspire.apworld (zip must contain a top-level "devilspire/" folder).
# Note: for official packaging use Archipelago's Launcher "Build APWorlds" (it adds the container version fields).
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$root/build"
out="$root/build/devilspire.apworld"
rm -f "$out"
cd "$root/worlds-src"
if command -v zip >/dev/null; then
  zip -r -q "$out" devilspire -x '*/__pycache__/*' '*.pyc'
else
  nix shell nixpkgs#zip -c zip -r -q "$out" devilspire -x '*/__pycache__/*' '*.pyc'
fi
echo "built $out"
