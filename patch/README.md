# Devil Spire Archipelago patch

Fan-made, unofficial. Patches a **copy** of your own `data.win` (never the Steam install, never committed/distributed).

## Player install (`/auto_patch` in the client)
Players do not run UndertaleModCli. The apworld ships `data/devilspire.bsdiff4` + `data/patch.json` (original sha256, current patched sha256, `known_patched_sha256` = all builds listed in `patch/KNOWN_PATCHED_SHA256`), built by `scripts/build_apworld.sh` (-> `scripts/make_patch.py`: bsdiff4 from pristine `game-copy/data.win` to `game-copy/data_patched.win`, self-checked, appends the new hash to KNOWN_PATCHED_SHA256; patch outputs are git-ignored). bsdiff4 is an Archipelago core requirement.
Client commands (`worlds-src/devilspire/auto_patch.py`), game folder found in Steam libraries (default roots + `libraryfolders.vdf`; Windows also the registry) unless given:
- `/auto_patch [force] [dir]`: original -> backup `data.win.orig` (only written when missing; an existing invalid file is moved to `data.win.orig.invalid`, a valid one is never overwritten), patch in memory, verify, write `data.win.ap-tmp`, fsync, atomic rename, verify, write `ap_patch_info.json`. Current patch -> no-op (`force` re-patches from backup). Older known patch -> re-patch from the valid backup. Unknown hash -> refused, nothing changed.
- `/restore [dir]`: backup verified -> atomically put back as data.win -> verify -> only then delete backup + `ap_patch_info.json`. Missing/invalid backup -> error pointing to Steam "Verify integrity of game files".
- `/patch_status [dir]`.
Changing the patch (ApPatch.csx / GML): rebuild `game-copy/data_patched.win` with `apply_patch.sh`, then `scripts/build_apworld.sh`.

## Client health checks (every 10 s, `health.py`)
data.win of the Steam install (game dir remembered from `/auto_patch` via Archipelago's persistent store, else found in Steam libraries; re-hashed only when mtime/size change) is not the current build; the newest `S|<protocol>` line differs from `PATCH_PROTOCOL`; files in the original `Devil_Spire` folder change while the client runs (= unpatched game played); `steam_autocloud.vdf` in `Devil_Spire_AP`. Each warning is logged once per change.
Non-ASCII save paths: client side tested (accented/CJK dirs). GMS1's runner uses the same relative-file mechanism for the game's own saves, so if vanilla saves work, AP files work; GMS1 itself with non-ASCII `%APPDATA%` is untested here.

## Separate save folder
GEN8 has `UseAppDataSaveLocation`, so the GMS1 runner saves to `%APPDATA%\<GEN8 Name>` (FileName "Devil Spire", Name "Devil_Spire", DisplayName "Devil Spire"; the folder matches **Name**). ApPatch.csx sets Name to `Devil_Spire_AP`, so the patched game never touches the normal `Devil_Spire` saves. Runtime **UNTESTED** (confirmed in the patched data.win's GEN8 only).
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

## Files (all in the patched game's save dir; under Proton `.../compatdata/1861290/pfx/drive_c/users/steamuser/AppData/Roaming/Devil_Spire_AP/`)
Text, one record per line, fields separated by `|`.

### `ap_config.ini` (client -> game; re-read on every poll, so client and game can start in any order)
```
[ap]
death_link=1            ; 0/1
floor_check_step=1      ; 1 every floor, 5 every 5th, 10 every 10th, 0 off  (floor N counts if (N-1) mod step == 0)
base_id=38470000         ; apworld BASE_ID 
poll_frames=30          ; optional, default 30
slot_id=<seed>:<team>:<slot>   ; multiworld identity (see "Multiworld identity" below)
```
Client mapping from slot_data `floor_checks`: 0->1, 1->5, 2->10, 3->0.

### `ap_out.txt` (game -> client, append-only)
- `L|<location id>|<slot_id>` boss cleared (`base_id + (N-9)/10`, floors -9..-99) or floor reached (`base_id + 100 + N-1`)
- `G|1|<slot_id>` goal: Rhamdon defeated (L/G carry the slot id the game belonged to; empty before the first connection)
- `D|<cause>` player died (only when death_link=1 and the death was not caused by an incoming DeathLink)
- `X|<text>` informational (death caused by DeathLink, DeathLink ignored without active run, slot adopted/changed); `N|1|..` new Descent run started; `S|<protocol>|..` patch started (protocol 3 = this build; the client warns on mismatch, `PATCH_PROTOCOL` in constants.py); `E|..` error
The client rescans the WHOLE file on every (re)connect (the server ignores duplicate checks), so checks made while the client was closed or disconnected are never lost; while connected it tails by byte offset (reset when the file shrinks or is replaced). DeathLink lines found in a rescan are historic and not re-sent. L/G lines tagged with another slot id are ignored. The client may move the file away (seed switch).

### `ap_in.txt` (client -> game; client rewrites the WHOLE file atomically: write tmp, rename)
- `I|<index>|<item id>|<item name>|<sender>`  full received-items list, indexes 0,1,2,... contiguous, in AP order. Game stores them by index and ignores indexes it already has.
- `D|<seq>|<text>`  DeathLink events; `seq` strictly increasing. On the first poll after start the game adopts the max seq (old events are not replayed); a higher seq kills the player only during an active run inside the tower (Descent, `rom_dungeon`, level < 0, `ap_granted >= 0`, alive); otherwise it is ignored, never queued (`X|deathlink ignored`).
- Indexes are stable: the client keeps the (item, location, player) order in `ap_client_state.json` and only appends, so a server that lost items (crash before autosave) and re-sends them in another order cannot shift indexes.

### `ap_souls_granted.txt` (game-private)
Line 1: highest received-item index whose **Pouch of Souls** was already granted (-1 = none); line 2: `slot_id`. Souls live in the vault (persist across deaths), so each Pouch (by received index) is granted only ONCE; re-applying the list on a new run skips it silently. Reset: automatically when `ap_config.ini` has a `slot_id` that differs from line 2, and by the client on a seed switch (file moved to the backup). Builds before 37b2dda4 parsed "-1" as 1; the client resets an untagged file to -1 on the first connection. Gold, orbs, etc. keep re-granting each run.

### `ap_granted.txt` (game-private)
Line 1: number of received items already granted to the CURRENT run (line 2: slot id of that run; a different configured slot at start => -1); `-1` = no AP run active (set on death, or unknown/legacy save). A new character (`ap_new_run`) sets it to 0, so ALL received items become pending again. They are applied ONLY when the player opens the Archipelago chest (below), in index order. At most 100 items are granted per chest open ("more items waiting, open again"). Ungrantable items (inventory/grimoire full) stop the batch (message "open again"); retried on 5 chest opens, then skipped (`E|skipped...`). After granting in the camp the chest also calls `save_souls(); save_game(mode)`, so quitting at the camp and choosing Continue neither loses nor re-grants items (the game itself only saves on floor change). Game restart mid-run: `ap_granted` persists, `ap_in` indexes are re-read from 0, only indexes >= ap_granted are pending.

### Multiworld identity
`slot_id` = `<seed name>:<team>:<slot>` (client: `make_slot_id`), stored in `ap_client_state.json` (client) and `ap_config.ini`, `ap_granted.txt`, `ap_souls_granted.txt` (game).
- Client, first connection for a save dir (no state file): adopts existing files (offline checks sent).
- Client, same slot: nothing reset. Different slot: moves `descent_character.ini, corpse.ini, ap_granted.txt, ap_souls_granted.txt, ap_out.txt, ap_in.txt, ap_config.ini, ap_client_state.json` to `ap_backup/<time>_<old slot>/` (never deleted; `souls.ini`/`unlocks.ini` stay), then writes the new config. It does not write `ap_in.txt` until the first ReceivedItems after Connected.
- Game (`ap_slot_check` each poll): empty session slot + configured X => adopt X. Session slot X, configured Y => **stale** until restart: no L/G/D lines, `ap_in.txt` ignored, chest refuses, `ap_granted=-1`, message "Quit and restart the game". On the next start the old run (if the game re-saved it) is inactive; a New Game starts the new multiworld.

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
