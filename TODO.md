# Devil Spire x Archipelago - TODO

Fan-made, unofficial. Protocol, file formats and patch details: [patch/README.md](patch/README.md). Research: [docs/](docs/).
**The patched game has never been run yet; everything in-game is untested.**

## Decisions
- Patched game = your own Steam `data.win`, patched in place by the client's `/auto_patch` with a bsdiff4 patch shipped in the apworld (backup `data.win.orig`, `/restore`, Steam verify as fallback). Separate save folder `Devil_Spire_AP` (GEN8 Name). No game files or patch in git.
- Single game mode "Archipelago" (= Descent, 100 floors). Goal: beat the final boss (Rhamdon, floor -100).
- Checks: boss kills + "Reach Floor -N" (option `floor_checks`, default every floor; Golems = one check; -99 gauntlet counts as both).
- No depth-key gating: everything reachable from the start; boost item pool (110 items, see docs/item-catalog.md); traps via `trap_percentage`.
- Roguelike loop: death resets the run, all received items are re-granted at the camp chest; checks persist. Souls granted once per slot.
- DeathLink: yes. Transport: text files in the game's save dir (client <-> game).
- Base ID **38,470,000** (block ..38,470,999; bosses +0..99, floors +100..199, items +500+code). Old yamls/seeds are incompatible.
- Min Archipelago 0.6.8; world_version 0.1.0. License: MIT.

## Done
- [x] **Reverse engineering:** data.win dumped/analysed with UndertaleModCli; save, boss, goal and hook notes in docs/.
- [x] **Apworld:** `worlds-src/devilspire` (items, locations, regions, options, rules, slot_data, example yaml, 38 tests, sample Generate OK); `scripts/build_apworld.sh`.
- [x] **Patch:** `patch/ApPatch.csx` + GML (boss/floor/goal/death emission, item polling, per-run re-grant, grant effects for all item types, `ap_config.ini`).
- [x] **Client:** "Devil Spire Client" Launcher component (`ds_client.py`, `file_protocol.py`, `client/`); 16 unit tests + local e2e.
- [x] **Single mode "Archipelago":** other modes hidden, "Descent" renamed, Extreme/Nightmare unlocked without prices.
- [x] **Camp chest:** fixed spot next to the bonfire in the pre-tower camp; grants received items, re-arms for mid-run items.
- [x] **No-gating boost pool:** keys and tier rules removed; new item ids and grant code.
- [x] **Install via client:** `/auto_patch [force] [game dir]`, `/restore`, `/patch_status` (Steam library detection incl. libraryfolders.vdf, hash checks, verified backup, atomic replace, upgrade from older builds via `patch/KNOWN_PATCHED_SHA256`); patch built by `scripts/build_apworld.sh`; unit tests + e2e on a temp copy of the game.
- [x] **Separate saves:** GEN8 Name `Devil_Spire` -> `Devil_Spire_AP`; client looks in all Steam libraries' Proton prefixes and %APPDATA%.
- [x] **Docs:** README, player guide, host guide.
- [x] **License:** MIT.

## To test in-game
- [ ] Title -> New Game -> character creation goes to mode 1; Continue shows the Archipelago save; no way to other modes (gamepad too).
- [ ] Boss checks (each boss, Golems, -99 gauntlet) reach the client.
- [ ] Floor -100: goal fires and the client reports completion.
- [ ] Item effects: stat orbs, stat point, gold/stone/souls, potion packs, spell pages (grimoire full), equipment tiers, ring.
- [ ] Traps (Ambush, Plague, Pickpocket) and DeathLink send/receive.
- [ ] Gear clutter: inventory/encumbrance with equipment re-grants; stat/level interaction of re-granted orbs.
- [ ] Chest edge cases: reachable (not inside decor), opens, re-arm for mid-run items, after death + new character, Continue from camp save, souls once across deaths, slot reset.
- [ ] First-ever character (tutorial skips the camp): how does the player get the chest?
- [ ] Client with the real game: save-folder detection, reconnect, items not duplicated on reload.

## After a full run
- [ ] Add a difficulty slot option (default Extreme).
- [ ] Decide equipment re-grant volume and tier levels.
- [ ] "Sent item" popups showing the sender.

## Release prep
- [ ] Test `/auto_patch` / `/restore` on real Windows (Steam path/registry detection, Program Files permissions).
- [ ] In-game: patched game really saves to `Devil_Spire_AP` (Proton and Windows) and leaves `Devil_Spire` alone; Steam Cloud behaviour.
- [ ] Test Launcher "Build APWorlds" and loading the apworld in a clean Archipelago install.
- [ ] Check with the Devil Spire developer (is publishing the apworld with the bsdiff4 patch OK?).
- [ ] Decide whether to publish.
- [ ] Other game builds: supported build is only the Steam build of 2026-10-11 (sha256 44df3801...c9b4); itch/GOG may differ and are refused.
- [ ] GitHub Release workflow (apworld only); bump `world_version` when the patch changes.

## Later / optional
- [ ] Faster transport (local TCP socket instead of files) if latency matters.
- [ ] Per-slot patch file (APContainer) from generation.
- [ ] Setup notes for NixOS/Proton; PR to Archipelago supported-games list.
- [ ] More location types (chests, NPC quests, shops).
