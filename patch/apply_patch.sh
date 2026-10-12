#!/usr/bin/env bash
# Apply the Archipelago patch to a COPY of data.win.  Usage: patch/apply_patch.sh <pristine data.win> <output data.win>
# Never point <output> at the original game install.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
in="${1:?usage: apply_patch.sh <in data.win> <out data.win>}"; out="${2:?usage: apply_patch.sh <in> <out>}"
[ "$(readlink -f "$in")" != "$(readlink -f "$out")" ] || { echo "in and out must differ" >&2; exit 1; }
case "$(readlink -f "$out")" in */steamapps/common/*) echo "refusing to write into the Steam install" >&2; exit 1;; esac
run() { if command -v UndertaleModCli >/dev/null; then UndertaleModCli "$@"; else nix shell nixpkgs#undertalemodcli -c UndertaleModCli "$@"; fi; }
run load "$in" -s "$here/ApPatch.csx" -o "$out" -f </dev/null
echo "wrote $out"
