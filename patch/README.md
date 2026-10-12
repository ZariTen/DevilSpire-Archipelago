# Devil Spire Archipelago patch

Fan-made, unofficial. Patches a **copy** of your own `data.win` (never the Steam install, never committed/distributed).
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
- `obj_god_Step_1`: `ap_poll()` every step (does work every `poll_frames` steps).

## Files (all in the game's save dir; under Proton `.../compatdata/1861290/pfx/drive_c/users/steamuser/AppData/Roaming/Devil_Spire/`)
Text, one record per line, fields separated by `|`.

### `ap_config.ini` (client -> game, read once at game start)
```
[ap]
death_link=1            ; 0/1
floor_check_step=1      ; 1 every floor, 5 every 5th, 10 every 10th, 0 off  (floor N counts if (N-1) mod step == 0)
base_id=7470000         ; apworld BASE_ID (placeholder)
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

### `ap_granted.txt` (game-private)
Number of received items already granted to the CURRENT run; `-1` = no AP run active (set on death, or unknown/legacy save). A new character (`ap_new_run`) sets it to 0, so ALL received items are re-applied (index order, up to 8 per poll). Ungrantable items (inventory full/weight) are retried 5 polls then skipped (`E|skipped...`).

## Item ids (relative to `base_id + 500`; full table and effects in docs/item-catalog.md)
No depth keys / gating (all floors reachable; removed 2026-10-11). 100-103 Orb of STR/INT/VIT/AGI (+3 stat), 104 Stat Point, 110 Yellow Orb (150-450 gold), 111 Gold Hoard (1000), 112 Blue Orb (random stone 0-35), 113 Pouch of Souls (+100), 120/121 Red/Blue Potion Pack (3x), 122 White Potion, 130/131/132 Spell Page Basic/Advanced/Master, 140-142 Weapon Lv25/50/75, 143-145 Armor Piece, 146-148 Accessory, 149/150 Shield Lv25/50, 151 Mystic Ring, 200 Ambush / 201 Plague / 202 Pickpocket trap.
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
