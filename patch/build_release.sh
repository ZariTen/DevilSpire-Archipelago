#!/usr/bin/env bash
# Build the player-facing patcher binaries into release/ (git-ignored; publish via GitHub Releases).
#   patch/build_release.sh [pristine data.win] [patched data.win]
# Defaults: game-copy/data.win and game-copy/data_patched.win (rebuilt from pristine with apply_patch.sh if missing/--rebuild).
# Needs go (uses `nix shell nixpkgs#go` if not on PATH). Never writes to the game install.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
here="$root/patch"
rebuild=0; args=()
for a in "$@"; do [ "$a" = "--rebuild" ] && rebuild=1 || args+=("$a"); done
pristine="${args[0]:-$root/game-copy/data.win}"
patched="${args[1]:-$root/game-copy/data_patched.win}"
expected="$(tr -d ' \n' < "$here/EXPECTED_ORIGINAL_SHA256")"
got="$(sha256sum "$pristine" | cut -d' ' -f1)"
[ "$got" = "$expected" ] || { echo "pristine data.win hash $got != expected $expected" >&2; exit 1; }
if [ "$rebuild" = 1 ] || [ ! -f "$patched" ]; then "$here/apply_patch.sh" "$pristine" "$patched"; fi
ver="$(sed -n 's/.*"world_version": *"\([^"]*\)".*/\1/p' "$root/worlds-src/devilspire/archipelago.json")"
gorun() { if command -v go >/dev/null; then "$@"; else nix shell nixpkgs#go -c "$@"; fi; }
rel="$root/release"; mkdir -p "$rel"
cd "$here/patcher"
export CGO_ENABLED=0 GOFLAGS=-trimpath
gorun go run ./cmd/mkdelta "$pristine" "$patched" cmd/patcher/delta.bin
gorun env GOOS=linux   GOARCH=amd64 go build -ldflags "-s -w -X main.version=$ver" -o "$rel/devilspire_ap_patcher"     ./cmd/patcher
gorun env GOOS=windows GOARCH=amd64 go build -ldflags "-s -w -X main.version=$ver" -o "$rel/devilspire_ap_patcher.exe" ./cmd/patcher
rm -f cmd/patcher/delta.bin   # derived from game data: keep it out of the working tree (it is embedded in the binaries)
cp "$root/build/devilspire.apworld" "$rel/" 2>/dev/null || true
(cd "$rel" && sha256sum devilspire_ap_patcher devilspire_ap_patcher.exe > SHA256SUMS)
ls -l "$rel"
