#!/usr/bin/env bash
# Apply the Archipelago patch to a COPY of data.win.  Usage: patch/apply_patch.sh <pristine data.win> <output data.win>
# Never point <output> at the original game install.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
in="${1:?usage: apply_patch.sh <in data.win> <out data.win>}"; out="${2:?usage: apply_patch.sh <in> <out>}"
[ "$(readlink -f "$in")" != "$(readlink -f "$out")" ] || { echo "in and out must differ" >&2; exit 1; }
case "$(readlink -f "$out")" in */steamapps/common/*) echo "refusing to write into the Steam install" >&2; exit 1;; esac
py() { if command -v "${PYTHON:-python3}" >/dev/null; then "${PYTHON:-python3}" "$@"; else nix shell nixpkgs#python3 -c python3 "$@"; fi; }
# title-screen label, derived from world_version + a hash of the patch sources (see scripts/mod_label.py)
export DS_AP_MOD_LABEL="$(py "$here/../scripts/mod_label.py")"
echo "mod label: $DS_AP_MOD_LABEL"
run() { if command -v UndertaleModCli >/dev/null; then UndertaleModCli "$@"; else nix shell nixpkgs#undertalemodcli -c UndertaleModCli "$@"; fi; }
run load "$in" -s "$here/ApPatch.csx" -o "$out" -f </dev/null
echo "wrote $out"
