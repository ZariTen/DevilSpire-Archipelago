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

## Item ids (relative to `base_id + 500`, matches worlds-src placeholders)
0-9 depth keys (counted only; floor gating NOT implemented), 100 Pouch of Souls (+100 souls), 101 Red Orb (+3 random stat), 102 Yellow Orb (100 gold), 103 Blue Orb (random stone), 200+ traps (ignored for now).

## Known gaps
Depth-key floor gating, traps, "sent item" popups, bosses skipped when `global.kills == 0` (game spawns no boss then), on-screen error handling. Receive/grant effects are guesses from reading the code dump.

## Launching a separate copy via a non-Steam shortcut
Add a `steam_appid.txt` containing `1861290` next to `Devil Spire.exe`; without it the game exits immediately when started as a non-Steam shortcut (verified 2026-10-11). Force a Proton version in the shortcut's Compatibility settings.
