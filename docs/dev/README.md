# Developer notes

- [patch.md](patch.md): building the patch, game changes, file protocol, client behaviour.
- [item-catalog.md](item-catalog.md): items, tiers and the pool.
- [game-notes.md](game-notes.md): game facts the patch relies on (modes, bosses, saves, death, items).
- Client code and tests: [client/README.md](../../client/README.md). Open work: [TODO.md](../../TODO.md).

Notes come from reading the decompiled game (Devil Spire v1.5999, GameMaker Studio 1) locally.
The dump lives in `game-copy/` and is git-ignored. Don't commit game code or assets.

## Why the install works this way
Other GameMaker Archipelago games (Undertale, Pizza Tower, Deltarune) also patch `data.win` with a binary diff.
No mod loader supports GameMaker Studio 1, so a DLL-based loader was ruled out.
We patch the Steam install in place, keep a backup, and use a separate save folder.

## References
- Archipelago docs: [world API](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/world%20api.md),
  [apworld format](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/apworld%20specification.md),
  [network protocol](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md).
- Undertale world (same install approach): `worlds/undertale` and `UndertaleClient.py` in the Archipelago repo.
- [UndertaleModTool](https://github.com/UnderminersTeam/UndertaleModTool) (nixpkgs: `undertalemodcli`).

## CI and releases
- CI (`.github/workflows/ci.yml`) runs the client and world unit tests against Archipelago 0.6.8 on every push and PR.
  It has no patch data, so it can't build the apworld.
- Releases are made locally, because the patch is built from your own `data.win`:
  add a `## vX.Y.Z` section to `CHANGELOG.md`, set `world_version`, rebuild the patched copy, push main, then
  `PYTHON=/tmp/ap-venv/bin/python scripts/release.sh X.Y.Z` (needs `gh auth login`; 0.x versions are pre-releases).
