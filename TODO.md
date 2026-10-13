# TODO

Technical details: [docs/dev/patch.md](docs/dev/patch.md).
The patched game runs on the real Steam install (Proton). Boot, Archipelago mode and floor checks are confirmed.

## Decisions
- The client patches your own Steam `data.win` in place (`/auto_patch`, backup `data.win.orig`, `/restore`). No game files in git.
- Saves go to a separate folder, `Devil_Spire_AP`.
- One game mode, "Archipelago" (Descent, 100 floors). Goal: beat Rhamdon on floor -100.
- Checks: bosses and floors (`floor_checks`). No gating. 110 boost items ([item-catalog](docs/dev/item-catalog.md)). Traps via `trap_percentage`.
- Death starts a new run. Items are re-granted at the camp (weightless direct, equipment on the ground). Souls are granted once.
- Base ID 38,470,000. Minimum Archipelago 0.6.8. License MIT.

## To test in-game
- [ ] Title and new character go straight to Archipelago mode (also with gamepad).
- [ ] Boss checks (each boss, Golems, -99 gauntlet) and the goal on floor -100.
- [ ] Item effects, traps and DeathLink.
- [ ] Camp items: ground spread is tidy and reachable (not in decor); 100+ items; Continue doesn't double or lose items.
- [ ] Mid-run items: equipment drops at your feet; untaken items follow to the next floor. Camp leftovers are dropped on entering the tower.
- [ ] First-ever character (the tutorial skips the camp).
- [ ] Client with the real game: reconnect, no duplicate items, seed switch, health warnings.
- [ ] Non-ASCII Windows user name.

## Before release
- [ ] Test `/auto_patch` and `/restore` on Windows.
- [ ] Confirm saves stay in `Devil_Spire_AP` on Windows; check Steam Cloud.
- [ ] Load the apworld in a clean Archipelago install.
- [ ] Ask the Devil Spire developer about publishing the patch.
- [ ] GitHub release workflow.

## Later
- [ ] Difficulty option (default Extreme).
- [ ] Tune equipment re-grants and tier levels.
- [ ] "Sent item" popups.
- [ ] More location types (chests, quests, shops).
