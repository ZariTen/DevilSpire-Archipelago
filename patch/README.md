# Devil Spire Archipelago patch

Fan-made, unofficial. Patches a **copy** of your own `data.win` (never the Steam install, never committed/distributed).

## Player-facing patcher (releases)
Players do not run UndertaleModCli. `patch/build_release.sh` turns the output of `apply_patch.sh` into one self-contained executable per platform:
- `patch/patcher/delta` - tiny copy/add binary delta (stdlib only: zlib + suffix array for matching). `mkdelta` creates it from pristine -> patched `data.win` (self-checks), the patcher embeds it (`go:embed`, temp file `cmd/patcher/delta.bin`, git-ignored and removed after the build).
- `patch/patcher/cmd/patcher` - the player tool: `patch` (default) / `status` / `restore` / `version`. Verifies sha256 of data.win (`patch/EXPECTED_ORIGINAL_SHA256` = Steam build in game-copy), creates `data.win.orig` with O_EXCL (never overwrites), applies the delta to `data.win.ap-tmp`, verifies the result hash, fsyncs, atomically renames over `data.win`. `restore` renames `data.win.orig` over `data.win` after hashing it. Exit codes: 0 ok, 1 usage, 2 no data.win, 3 unsupported hash, 4 already patched/backup conflict, 5 I/O or permission, 6 backup missing/invalid.
- Build: `patch/build_release.sh [pristine] [patched] [--rebuild]` (needs Go; uses `nix shell nixpkgs#go`). Outputs to `release/` (git-ignored): `devilspire_ap_patcher` (linux/amd64), `devilspire_ap_patcher.exe` (windows/amd64), `SHA256SUMS`, copy of `build/devilspire.apworld`. Pure Go cross-compile, `CGO_ENABLED=0`.
- Publish via **GitHub Releases only**. The delta and binaries are derived from game data: never commit them (`release/`, `delta.bin`, `*.win` are in .gitignore). Whether publishing is OK is a licensing decision for the maintainer.
- Changing the patch (ApPatch.csx / GML) changes the patched hash: just rerun the build script. The pristine hash only changes if the game is updated.
- Tested: Linux binary on copies (patch, byte-identical to the apply_patch.sh output, restore, double patch, wrong hash, missing/bogus backup, read-only dir) and the .exe under wine64 11.0 (status/patch/double/restore).
STATUS: patch builds and the result loads/re-dumps in UndertaleModCli; **runtime behavior is UNTESTED** (game not run yet).

## Apply
```
cp "<steamapps>/common/Devil Spire/"* ~/Games/DevilSpire-AP/      # separate game copy
patch/apply_patch.sh ~/Games/DevilSpire-AP/data.win ~/Games/DevilSpire-AP/data_patched.win
mv data_patched.win data.win   # inside the copy, keep a pristine backup
```
(or directly: `UndertaleModCli load data.win -s patch/ApPatch.csx -o data_patched.win -f </dev/null`; `nix shell nixpkgs#undertalemodcli` on NixOS.)
The script refuses to run on an already patched file. `patch/gml/*.gml` are the new helper scripts (GMS1 syntax only).

## What it changes
- `obj_setup_Alarm_0`: `global.descent = 1` (Descent always unlocked) + `ap_init()` (reads `ap_config.ini`).
- `obj_enemy_Step_0` (`if (aux)` boss-floor block): `ap_boss_cleared()`.
- `next_floor`: `ap_floor_reached()` after the floor counter changed.
- `obj_rhamdon_Step_1`: `ap_goal()` right before `room = rom_ending;` (only Descent emits).
- `obj_player_Step_0` (hp==0 block): `ap_death_send()`.
- `obj_charcreation_Alarm_0`: `ap_new_run(mode)` before the first save of a new character.
- `obj_god_Step_1`: `ap_poll()` every step (does work every `poll_frames` steps; reads `ap_in.txt`, tracks the item list and DeathLink; **no longer grants items**).
- `obj_chest_Create_0`: `ap_chest = 0;` + branch to `ap_chest_init()` when `global.ap_chest_spawn` is set (Archipelago chest, no vanilla loot roll/key).
- `interact` (obj_chest case, opened state): `if (ap_chest) { ap_chest_open(); exit; }`.
- `obj_dungeoncreator_Step_0` (`dungeon == 0.5` branch, right after `create_village(1)`): `ap_chest_spawn()` (camp chest; no longer on floor -1).

## Files (all in the game's save dir; under Proton `.../compatdata/1861290/pfx/drive_c/users/steamuser/AppData/Roaming/Devil_Spire/`)
Text, one record per line, fields separated by `|`.

### `ap_config.ini` (client -> game, read once at game start)
```
[ap]
death_link=1            ; 0/1
floor_check_step=1      ; 1 every floor, 5 every 5th, 10 every 10th, 0 off  (floor N counts if (N-1) mod step == 0)
base_id=38470000         ; apworld BASE_ID 
poll_frames=30          ; optional, default 30
```
Client mapping from slot_data `floor_checks`: 0->1, 1->5, 2->10, 3->0.

### `ap_out.txt` (game -> client, append-only; client dedups / tracks its read offset)
- `L|<location id>` boss cleared (`base_id + (N-9)/10`, floors -9..-99) or floor reached (`base_id + 100 + N-1`)
- `G|1` goal: Rhamdon defeated
- `D|<cause>` player died (only when death_link=1 and the death was not caused by an incoming DeathLink)
- `X|<text>` informational (death caused by DeathLink); `N|1|..` new Descent run started; `S|1|..` patch started; `E|..` error
The client may truncate/delete the file at any time.

### `ap_in.txt` (client -> game; client rewrites the WHOLE file atomically: write tmp, rename)
- `I|<index>|<item id>|<item name>|<sender>`  full received-items list, indexes 0,1,2,... contiguous, in AP order. Game stores them by index and ignores indexes it already has.
- `D|<seq>|<text>`  DeathLink events; `seq` strictly increasing. On the first poll after start the game adopts the max seq (old events are not replayed); a higher seq later kills the player (when alive in the dungeon, Descent only).

### `ap_souls_granted.txt` (game-private)
Line 1: highest received-item index whose **Pouch of Souls** was already granted (-1 = none); line 2: `slot_id`. Souls live in the vault (persist across deaths), so each Pouch (by received index) is granted only ONCE; re-applying the list on a new run skips it silently. Reset: automatically when `ap_config.ini` has a `slot_id` (client writes `<seed name>:<slot>`) that differs from line 2; otherwise delete the file (e.g. `make_test_ap_in.sh --reset`) when starting a new multiworld. Gold, orbs, etc. keep re-granting each run.

### `ap_granted.txt` (game-private)
Number of received items already granted to the CURRENT run; `-1` = no AP run active (set on death, or unknown/legacy save). A new character (`ap_new_run`) sets it to 0, so ALL received items become pending again. They are applied ONLY when the player opens the Archipelago chest (below), in index order. Ungrantable items (inventory/grimoire full) stop the batch (message "open again"); retried on 5 chest opens, then skipped (`E|skipped...`).

## Item ids (relative to `base_id + 500`; full table and effects in docs/item-catalog.md)
No depth keys / gating (all floors reachable; removed 2026-10-11). 100-103 Orb of STR/INT/VIT/AGI (+3 stat), 104 Stat Point, 110 Yellow Orb (Gold) (150-450 gold), 111 Gold Hoard (1000), 112 Blue Orb (Stone) (random stone 0-35), 113 Pouch of Souls (+100), 120/121 Red/Blue Potion Pack (3x), 122 White Potion, 130/131/132 Spell Page Basic/Advanced/Master, 140-142 Weapon Lv25/50/75, 143-145 Armor Piece, 146-148 Accessory, 149/150 Shield Lv25/50, 151 Mystic Ring, 200 Ambush / 201 Plague / 202 Pickpocket trap.
Everything is re-granted on each new run (index order). Traps only fire when received live (`global.ap_live[idx]`, set by `ap_poll` for items arriving after the first read of `ap_in.txt`) and are consumed. Equipment/consumables are added with `add_inventory(it,-4,0)` (no encumbrance check; retried/skipped only when the 100 slots or the 24-slot grimoire are full). **All grant effects UNTESTED at runtime.**

## Known gaps
Trap/equipment runtime behaviour, "sent item" popups, bosses skipped when `global.kills == 0` (game spawns no boss then), on-screen error handling. Receive/grant effects are guesses from reading the code dump.

## Launching a separate copy via a non-Steam shortcut
Add a `steam_appid.txt` containing `1861290` next to `Devil Spire.exe`; without it the game exits immediately when started as a non-Steam shortcut (verified 2026-10-11). Force a Proton version in the shortcut's Compatibility settings.

## Single game mode "Archipelago" (2026-10-11)
Only Descent (internal `global.mode == 1`) is selectable and it is shown as **Archipelago**. Original modes: 0 Ascent, 1 Descent, 2 Chaos, 3 Arena, 4 Immortal, 5 Soul (+ difficulties Easy/Normal/Hard/Extreme/Nightmare, separate on the same screen).
- `obj_setup_Alarm_0`: default `global.mode = 1`. `obj_title_Step_0`: forces `global.mode = 1` on the mode-select screen. The screen is kept (it also holds difficulty/speed; difficulty kept unchanged, Extreme/Nightmare still show their UNLOCK prices): `buttonize_title` shows one greyed, inert "Archipelago" button (action 0, `nulled`), so the other modes cannot be selected or bought.
- Continue list only shows/considers `descent_character.ini` (other saves hidden, files untouched); labels "Archipelago (entrance|flr. N)".
- `mode_difficulty_floor` (HUD pause menu, char creation "Mode:", gameover, ending): "Descent" -> "Archipelago" (e.g. "Normal Archipelago 1x"). Mode description text on title: "Archipelago#Floors: 99...".
- Not changed: ini/save names, `global.mode` checks, `unlockable()` (never reached), dead code strings like "< Descent >" remain in the string table but are unreachable. Runtime **UNTESTED**.

## Starting chest (moved to the camp bonfire 2026-10-12; the floor -1 text below is superseded where it conflicts)
- **Location**: the pre-tower camp = the "village" (`dungeon == 0.5`, `global.level == 0.5`), built by `create_village(1)` from `obj_dungeoncreator` Step. Layout (fixed): `obj_bonfire` (0,0) [the fireplace], player arrival (0,212), tower door `obj_entrance` (0,-149), merchant (0,-320). Descent flow: new character -> level 0.5 (camp) -> `next_floor` -> floor -1. (First-ever character does the tutorial level 0 first, which goes straight to -1 and skips the camp.) `create_darkroom` (0.4) is the orb-crystal room (Soul mode), not used.
- `ap_chest_spawn()` runs right after `create_village(1)`: needs `global.mode == 1`, `global.level == 0.5`, `ap_granted >= 0` (not after death until a new character resets it). It creates the chest at the bonfire x/y plus the first free offset of a FIXED list (40,16), (-40,16), (40,-16), (-40,-16), (0,44), (56,0), ... checked with `place_free` and not on bonfire/entrance/tombstone/shade (strict pass also needs 10px free around; relaxed second pass). Expected spot: (40,16). Lid faces the arrival point. If none is free: no chest + `E|no free position...` in ap_out.txt. The chest is always present in the camp (even with nothing pending: "nothing new"); `ap_poll` re-arms it when items arrive.
- Floors -1.. no longer get a chest (random spawn removed); items arriving mid-run wait until the next camp visit (after death + new character).

### Older description (floor -1 version, superseded)
- Items are no longer auto-granted. At the end of floor generation `ap_chest_spawn()` creates an `obj_chest` (marked `ap_chest=1`, arena-chest textures `tex_chest*3` so it looks different, placeholder loot = 1 gold object for the floating visual, never picked up) on a random free spot 26-38 px from the player's spawn (0,0), found with `place_free` (+ not on stairs/trap/player, + 10px margin on the strict pass; relaxed second pass). If no spot: no chest, `E|no free position...` in ap_out.txt.
- Spawns on Descent floor -1 always, and on any later floor when received items are still pending (also after Continue). Not when `ap_granted == -1` (no active run, e.g. dead/legacy save).
- Use it like a normal chest: interact once to open (lid animation), interact again -> `ap_chest_open()` grants ALL pending items (souls once only, traps only if received live), plays the treasure sound and shows `Archipelago: received N items` (+ per-item messages stay off). Chest then stays open and empty.
- Items arriving mid-run stay pending; `ap_poll` re-arms the emptied chest of the current floor (closed again, new placeholder) so it can be opened again; otherwise they are given by the next floor's chest.

## Offline testing (no client)
1. `patch/make_test_ap_in.sh` (add `--reset` to also delete `ap_granted.txt`, `ap_souls_granted.txt`, `ap_out.txt`). It writes a 20-item `ap_in.txt` (orbs, stat point, gold, blue orb, 2x souls pouch, potions, spell page, gear, ring, one Ambush trap) and `ap_config.ini` (`slot_id=offline-test:Tester`) into the Proton save dir `.../compatdata/2579370111/.../Devil_Spire/` (originals kept as `*.bak`).
2. Start the game from the AP copy, New Game -> create a character -> you start in the tutorial/village; descend to floor -1.
3. Find the differently-tinted chest next to the stairs where you spawned; open it (interact twice). Expect `Archipelago: received 20 items`, stats/gold/potions/gear in inventory, +100 souls once (the second pouch is skipped), no trap (traps only fire when received while playing).
4. Die, create a new character: chest again grants everything except souls (check `ap_souls_granted.txt` = 7).
5. Mid-run: append a line `I|20|38470600|Orb of Strength|Tester` (id = 38470500 + code; 38470600 = Orb of Strength; the file index must continue 0..N contiguously) to `ap_in.txt` while playing; within ~1 s the chest re-arms (or appears next floor) and the new item is granted on opening; as a live item, an Ambush trap line (38470700) fires on opening.
Risky/untested: all of the above at runtime, chest placement collisions (place_free assumption), re-arm via `item = generate_gold(1)`, `exit` in Create_0 prepend, messages overlapping.
