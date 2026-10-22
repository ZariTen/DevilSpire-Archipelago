#!/usr/bin/env bash
# Build build/devilspire.apworld (zip with a top-level "devilspire/" folder) including the bsdiff4 game patch.
#   scripts/build_apworld.sh [pristine data.win] [patched data.win]
# Defaults: game-copy/data.win and game-copy/data_patched.win (make the latter with patch/apply_patch.sh).
# The patch is built by scripts/make_patch.py with $PYTHON (needs bsdiff4; default: python3 if it has it, else
# `nix shell` with python3 + bsdiff4). scripts/pack_apworld.py zips it like the Launcher's "Build APWorlds".
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
py="${PYTHON:-python3}"
run() {  # run a script with a python that has bsdiff4
  if command -v "$py" >/dev/null && "$py" -c 'import bsdiff4' 2>/dev/null; then
    "$py" "$@"
  else
    nix shell --impure --expr 'with import <nixpkgs> {}; python3.withPackages (p: [ p.bsdiff4 ])' -c python3 "$@"
  fi
}
run "$root/scripts/make_patch.py" "$@"
run "$root/scripts/pack_apworld.py"
