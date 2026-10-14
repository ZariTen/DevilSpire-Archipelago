# TODO

Technical details: [docs/dev/patch.md](docs/dev/patch.md).
The patched game runs on the real Steam install (Proton). A partial 2-player run went smoothly.

## Decisions
- The client patches your own Steam `data.win` in place (`/auto_patch`, backup `data.win.orig`, `/restore`). No game files in git.
- Saves go to a separate folder, `Devil_Spire_AP`.
- One game mode, "Archipelago" (Descent, 100 floors). Goal: beat Rhamdon on floor -100. Difficulty set by the yaml (default Extreme).
- Checks: bosses, every 2nd floor (`floor_checks`), one locked chest per floor, 18 shop stands. No gating.
- Items: 110-item template ([item-catalog](docs/dev/item-catalog.md)), extra slots scaled proportionally. Traps via `trap_percentage`.
- Death starts a new run. Items are re-granted at the camp (weightless direct, equipment on the ground). Souls once.
- Base ID 38,470,000. Minimum Archipelago 0.6.8. License MIT.

## To test in-game
- [ ] Boss checks (each boss, Golems, -99 gauntlet) and the goal on floor -100.
- [ ] Item effects, traps and DeathLink.
- [ ] Camp items: tidy ground spread, 100+ items, Continue doesn't double or lose items.
- [ ] Locked chests: one per floor with a reachable key (also the forced/placed one), AP item inside, check sent, normal once sent.
- [ ] Shop checks: icon, price 150, buy and steal send the check.
- [ ] Archipelago Item description ("X for Y (tag)") in shop and chest.
- [ ] "Sent X to Y" popups, capped on bulk sends.
- [ ] Difficulty locked on New Game and Continue; label "(AP)".
- [ ] Seed switch: title adopts live; a tower run stays stale until it ends; warnings show.
- [ ] Title shows "Connected" / "Client not connected"; no items before the client connects.
- [ ] First-ever character (the tutorial skips the camp).
- [ ] Non-ASCII Windows user name.

## Before release
- [ ] `/auto_patch` and `/restore` on Windows; saves stay in `Devil_Spire_AP`; Steam Cloud.
- [ ] Load the apworld in a clean Archipelago install.
- [ ] Ask the Devil Spire developer about publishing the patch.
- [ ] GitHub release workflow.

## Later
- [ ] More location types (quests).
