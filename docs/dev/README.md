# Developer notes

- [patch.md](patch.md): building the patch, game changes, file protocol, client behaviour.
- [item-catalog.md](item-catalog.md): items and how the game creates them.
- [locations-bosses.md](locations-bosses.md): boss and floor logic from the code dump.
- [descent-goal.md](descent-goal.md): Descent unlock and the ending.
- [save-and-hooks.md](save-and-hooks.md): save files, death, and hook points.
- Client code and tests: [client/README.md](../../client/README.md). Open work: [TODO.md](../../TODO.md).

These notes come from reading the decompiled original code (Devil Spire v1.5999, GameMaker Studio 1).
The dump lives in `game-copy/` and is git-ignored.

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
