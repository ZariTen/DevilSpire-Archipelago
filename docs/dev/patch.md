# Patch and file protocol

## Build
- Sources: `patch/ApPatch.csx` (UndertaleModTool script) and `patch/gml/*.gml` (GMS1 GML).
- Build the patched file from the original Steam `data.win` (sha256 in `patch/EXPECTED_ORIGINAL_SHA256`):
  `patch/apply_patch.sh game-copy/data.win game-copy/data_patched.win`
  (runs `UndertaleModCli load data.win -s ApPatch.csx -o out.win -f </dev/null`; NixOS: `nix shell nixpkgs#undertalemodcli`).
- `scripts/build_apworld.sh` makes `data/devilspire.bsdiff4` + `data/patch.json` (via `scripts/make_patch.py`) and zips `build/devilspire.apworld`.
  The patch files are git-ignored. Each new patched hash is added to `patch/KNOWN_PATCHED_SHA256`.
- Mod label (top-left of the title screen, also sent as `S|<protocol>|<label>`): `Archipelago v<world_version> (<id>)`.
  `<id>` = 7 hex of a sha256 over `ApPatch.csx`, `gml/*.gml` and `EXPECTED_ORIGINAL_SHA256` (`scripts/mod_label.py`).
  `apply_patch.sh` passes it in `DS_AP_MOD_LABEL`; `make_patch.py` checks it is in the patched file and stores it in
  `patch.json`. Same sources give the same label and the same patched file (no commit hash, so builds stay reproducible).
- After a GML change: bump `PATCH_PROTOCOL` in `constants.py` and the `S|<n>` line in `ap_init.gml`.

## Install (`auto_patch.py`)
- `/auto_patch`: checks the original hash, writes `data.win.orig` once (never over a valid backup), patches in memory,
  verifies, writes `data.win.ap-tmp`, renames it over `data.win`. Older builds of ours are re-patched from the backup.
- `/restore`: puts the valid backup back, verifies, deletes the backup.
- The game folder comes from the Steam libraries (`libraryfolders.vdf`; Windows registry) or the last `/auto_patch` folder.

## Game changes
- Save folder: GEN8 `Name` `Devil_Spire` -> `Devil_Spire_AP` (`UseAppDataSaveLocation` = `%APPDATA%\<Name>`).
- One mode: Descent (`global.mode = 1`), shown as "Archipelago"; other modes hidden; Descent unlocked.
- Hooks: `obj_setup_Alarm_0` -> `ap_init`; `obj_god_Step_1` -> `ap_poll`; `next_floor` -> `ap_floor_reached`;
  boss floor cleared (`obj_enemy_Step_0`) -> `ap_boss_cleared`; `obj_rhamdon_Step_1` -> `ap_goal`;
  player death -> `ap_death_send`; new character -> `ap_new_run`.
- Items (`ap_poll`, player alive in `rom_dungeon`, no `obj_dungeoncreator`): `ap_grant_pending` processes up to 100 per poll.
  Weightless (`ap_item_weighted` = 0: stat orbs/point, gold, Blue Orb stone, souls, Progressive Spellbook, traps) are applied directly.
  Weighted (potions 0.25 each, progressive gear, rings 0.1). Progressive: copy N = Nth in `ap_in` order (`ap_copies`); gear only if no later copy is received (best tier per run); ground key = index*10 + armor piece go to the ground list `global.ap_drops`.
- Ground items (`ap_drop_spawn`): native `obj_droppeditem` (`item = ap_drop_make(id)`), picked up with the game's `interact`/`get_item`.
  Camp: grid (20 px) around the arrival point (0,212); tower: grid (16 px) around the player. Spot must be free for the
  player's mask and not on decor/shades/bonfire/entrance/tombstones; else at the anchor. Max 60 on the ground.
  `obj_droppeditem` gets `ap_idx` (Create); its Destroy (= picked up) calls `ap_drop_taken`. Leaving the room does not fire
  Destroy, so untaken mid-run items spawn again on the next floor. Leaving the camp (`ap_leave_room`, prepended to
  `next_floor`) forfeits untaken camp items for this run. The item is rolled again on each spawn.
- Commit: `ap_granted.txt` is only written next to the character save (`next_floor`, camp after granting, new run,
  death). Quit + Continue rolls back both together: nothing lost, nothing doubled. Mid-floor progress is lost like vanilla.

## Chest and shop checks
- Chests (`ap_chest_check`, from `interact`): when the player opens a chest, or uses one that was generated open.
  Once per chest (`ap_counted`); mimics (`obj_skullcrab` inside) and camp chests don't count. Up to `chest_checks`
  (ap_config, 0-5) per 10-floor band, cumulative over runs.
- Shops: Descent shop floors are |floor| mod 10 == 0 without a boss (-10..-90). `ap_shop_setup` runs after the
  8 stands are created and puts an "Archipelago Item" (obj_misc type 77, `ap_make_apitem`) on up to 2 stands, one per
  unsent check, price 150. `get_item` sends the check for it (`ap_shop_item`), so buying and stealing both work.
- Icon: `spr_apicon` (16x16) and `spr_Dapicon` (64x64, 3D) imported by `ApPatch.csx` from `patch/assets/*.png`
  (`make_ap_icon.py` draws them). The PNGs are part of the mod label hash.

## Files in the save folder
Text files, one record per line, fields split by `|`.

`ap_config.ini` (client -> game, re-read every poll):
```
[ap]
death_link=1
floor_check_step=2      ; 1, 2, 5, 10, or 0 = off (floor N counts if (N-1) mod step == 0)
chest_checks=3          ; chest checks per 10-floor band (0 = off)
base_id=38470000
slot_id=<seed>:<team>:<slot>
```

`ap_out.txt` (game -> client, append only):
- `L|<location id>|<slot_id>` check. Boss: `base_id + (N-9)/10`. Floor -N: `base_id + 100 + N-1`.
  Chest: `base_id + 200 + band*5 + k` (band = (N-1) div 10). Shop: `base_id + 250 + (N/10-1)*2 + stand` (N = 10..90).
- `G|1|<slot_id>` goal. `D|<text>` death (DeathLink). `S|<protocol>|<mod label>` game started (the client warns on a mismatch).
- `N|..` new run, `X|..` info, `E|..` error.
- The client rescans the whole file on every connect (the server ignores duplicates).
  Lines tagged with another `slot_id` are ignored. Old DeathLink lines are not re-sent.

`ap_in.txt` (client -> game, whole file rewritten atomically):
- `I|<index>|<item id>|<name>|<sender>` all received items. Indexes never change: the client stores the
  (item, location, player) order in `ap_client_state.json` and only appends.
- `D|<seq>|<text>` DeathLink. Kills only during an active run inside the tower; otherwise ignored.

Game-private: `ap_granted.txt` (items processed for the current run, `-1` = no run; line 2 = slot_id; line 3 = ground indexes `i,j,k`),
`ap_souls_granted.txt` (souls are granted once per slot; line 2 = slot_id),
`ap_heartbeat.txt` (`counter|slot_id|name`, rewritten by the client every 3 s while connected and synced; the game counts it as connected if it changed in the last 10 s, and gives no items until it has changed once this session),
`ap_checks.txt` (chest checks sent per band `c0,..,c9`; 18 shop flags; slot_id; cumulative per slot, reset by the client on a seed switch).

## Multiworld switch
- First connection for a save folder: existing files are kept and offline checks are sent.
- Different `slot_id`: the client moves the character and `ap_*` files to `ap_backup/<time>_<old slot>/`.
  `souls.ini` and `unlocks.ini` stay.
- A running game that sees a new `slot_id` stops sending checks and reading items until it restarts.

## Client health warnings (`health.py`, every 10 s)
`data.win` not the current build; game protocol mismatch; changes in the original `Devil_Spire` folder
(unpatched game being played); `steam_autocloud.vdf` in `Devil_Spire_AP`.

## Item ids
`base_id + 500 + code`: 100-103 stat orbs (STR/INT/VIT/AGI), 104 stat point, 110 Yellow Orb (gold), 111 Gold Hoard,
112 Blue Orb (stone), 113 Pouch of Souls, 120/121 Red/Blue Potion Pack, 122 White Potion, 151 ring, 160-164 Progressive Weapon/Armor/Shield/Accessory/Spellbook, 200-202 traps. Effects: [item-catalog.md](item-catalog.md).

## Known gaps
In-game behaviour is mostly untested (item effects, traps, ground item placement). Bosses don't spawn if the player
has no kills on the run (`global.kills == 0`). Test helper: `patch/make_test_ap_in.sh` writes a sample `ap_in.txt`.
