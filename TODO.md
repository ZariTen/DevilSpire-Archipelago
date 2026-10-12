# Devil Spire x Archipelago - Plan / TODO

Target: GameMaker Studio 1 game (Windows exe via Proton on NixOS). Files: data.win (~44 MB), audiogroup*.dat, Devil Spire.exe. Legend: **[U]** = unverified assumption to check. Sources and details in docs/research-notes.md.
Do NOT modify the original install: work on a copy (e.g. ~/Games/DevilSpire-AP/) and keep a pristine data.win backup + checksum.

## Recommended architecture (TL;DR)
1. **apworld** `devilspire` (Python) for generation: items, locations, regions, options, rules, docs, tests.
2. **GML patch** applied to a *copy* of data.win via UndertaleModCli script: hooks at location pickup / boss kill / flags, an item-receive handler, goal and (optional) death hooks.
3. **External Python client** (CommonContext subclass, like Undertale's) talking to the AP server over websocket, and to the game via **files** (phase 1, simplest, robust under Proton) with optional upgrade to **local TCP socket** (GMS1 `network_*` [U]) if latency matters.
Why: GMS1 has no known websocket support (the public GML AP sample requires GM >= 2.2.1), so the game should never speak the AP protocol itself.

## Phase 0 - Environment (NixOS)
- [ ] Create flake/devshell: python3 (match Archipelago's supported version [U]), git, undertalemodcli (nixpkgs `undertalemodcli`; or NUR `utmt-cli`), dotnet runtime if needed, protontricks/umu optional.
- [ ] Clone ArchipelagoMW/Archipelago (source install) for world development + `Launcher.py "Build APWorlds"`.
- [ ] Copy the game to a work dir; record sha256 of data.win, exe. Note Steam build id [U].
- [ ] Find the Proton prefix (compatdata/<appid>) and where the game writes saves/ini (run once, `find -newer`).

## Phase 1 - Reverse engineering
- [ ] Open data.win with UndertaleModCli (load + save unchanged; diff to prove round-trip works for this GMS1 build). If UTMT fails on this version, record error and investigate other tools. [U]
- [ ] Dump everything: code (GML decompile), objects, rooms, scripts, sprites names, strings, to a git-ignored folder (e.g. dump/ - don't commit game assets/code; only notes).
- [ ] Identify game version/bytecode version from GEN8 chunk; record in notes.
- [ ] Save system: find save/load scripts; what is persisted (ini? file_bin? globals?); where files live; slot count; whether saves are per-character (a char-creation music `bgm_charcreation` suggests character creation [U]).
- [ ] Item model: how items are defined (ds_map/arrays/objects?), IDs, inventory add function, equipment, consumables, currency, keys/quest items.
- [ ] Pickup logic: chests, ground items, NPC gifts, shops, enemy drops, quest rewards - find the central "give item" function(s) to hook.
- [ ] World structure: rooms list, areas (town, forest, cave, dungeon, lava, ... from bgs_*/bgm_* names [U]), doors/gates/keys, one-way paths, shortcuts, the "spire" progression.
- [ ] Persistent flags: how opened chests / killed bosses / switches are stored (global arrays, ds_map, ini) -> needed to detect checks and to avoid re-sending.
- [ ] Bosses and endings: boss objects, kill events, final boss / ending trigger, multiple endings?
- [ ] Death/game-over handling (`bgm_gameover`): where HP hits 0, what is lost (for DeathLink send/receive).
- [ ] Respawn/save-and-quit behaviour (AP assumes player can return to the start region).
- [ ] Produce `docs/locations-draft.csv` and `docs/items-draft.csv` (name, room, object id/flag, description, requirements).
- [ ] Note anti-cheat/Steam hooks (steam_api.dll, achievements) - make sure patch doesn't break launching via Steam. [U]
- [ ] Check legal/ethical: distribute only the patch/script, never data.win or assets.

## Phase 2 - Design
- [ ] Decide location set: chests / pickups / boss kills / NPC quests / shop slots / levelups? Start with chests + bosses, expand later.
- [ ] Decide item set: progression (keys, abilities, gear gating areas), useful (upgrades), filler (consumables/gold), traps (optional). Mark classification for each.
- [ ] Goal: define victory (final boss kill / ending). Client sends `StatusUpdate` CLIENT_GOAL (events alone don't complete goals).
- [ ] Regions & logic: build region graph from rooms; per-entrance rules; identify sequence breaks and soft-locks; decide whether logic assumes character class/stats [U if classes exist].
- [ ] Options (YAML): goal, location groups included, item/gold scaling, starting items, death_link, trap %, difficulty, class? etc.
- [ ] Items for other players' locations: how the game shows "sent item X to Y" (text box / popup).
- [ ] Received item handling: what happens for unique items given while inside a menu/room; duplicates; save-reload (must be idempotent via received item index).
- [ ] ID plan: base id (pick unique, e.g. 7_000_000+ and check no clash [U]), contiguous tables kept in one data file.
- [ ] Plan for start inventory and `remote_start_inventory` handling.

## Phase 3 - APWorld
Layout (inside Archipelago/worlds/devilspire/ during dev):
```
devilspire/
  __init__.py      # DevilSpireWorld(World), WebWorld, Item/Location subclasses, fill_slot_data
  items.py         # item table (name, id, classification, count)
  locations.py     # location table (name, id, region, flag/key)
  regions.py       # regions + entrances
  rules.py         # access rules
  options.py       # PerGameCommonOptions dataclass
  client.py        # (or in-game bridge client, launcher component)
  archipelago.json # game, minimum_ap_version, world_version, authors
  docs/en_Devil Spire.md        # game info
  docs/setup_en.md              # setup guide
  test/__init__.py, test_access.py, test_options.py
  data/ (patch script, GML snippets)  # no game assets
```
- [x] Floor checks (100 floors, granularity option), golems as single check, filler re-grant documented.
- [~] Implement items/locations tables (PLACEHOLDER skeleton done in worlds-src/devilspire; real data pending RE) from phase 1 CSVs (single source of truth shared with the patch generator).
- [x] World class: game name, item_name_to_id, location_name_to_id, create_regions/items/rules, create_item, filler via get_filler_item_name, completion_condition, item_name_groups.
- [x] Events for logic (bosses, key doors) as id=None items on id=None locations; goal via victory event.
- [x] Options file with docstrings (rich_text_options_doc), presets optional.
- [x] fill_slot_data: only options the client/patch needs (death_link, goal, etc.); use LocationScouts for item info.
- [x] Docs: game info page, setup guide, WebWorld Tutorial entry.
- [x] Tests: WorldTestBase (4 test classes pass; run: symlink into AP worlds/ + pytest), assertAccessDependency per gated area; run AP's `python -m unittest` for the world; also generation smoke tests with various option combos (all options, minimal).
- [~] Build `.apworld` -- scripts/build_apworld.sh zips to build/devilspire.apworld; Launcher "Build APWorlds" not yet tried with Launcher "Build APWorlds" and test loading by dropping into a clean AP install's worlds folder.

## Phase 4 - In-game integration / client

### Options considered
| Approach | Pros | Cons |
|---|---|---|
| A. Files bridge: GML patch reads/writes small text files; Python client watches them (Undertale model) | Works w/ any GM version, no DLL; trivial under Proton (shared filesystem); easy to debug; proven precedent (Undertale) | Polling latency (~0.5-1s fine), file-lock races, must find the right folder inside the prefix |
| B. Local TCP socket from GML (`network_create_socket`/`network_connect` raw) to a Python bridge, bridge talks AP websocket | Low latency, bidirectional, no file races | GMS1 network API details/behavior unverified [U]; needs own framing; Wine networking quirks [U] |
| C. Websocket client directly in GML (like PrintOmnivore20 sample) | No external process | Sample needs GM >= 2.2.1 -> not available in GMS1; would need custom DLL |
| D. Custom DLL via external_define (e.g. websocket/http DLL) loaded in Proton | In-game AP client possible | Must ship a 32/64-bit DLL matching exe arch [U], DLL arg limits (real/string only), Wine DLL loading, security/AV friction, more maintenance |
| E. Memory reading/writing from external process | No game patch | Fragile, offsets break, Proton process access hard, ASLR; not recommended |

**Recommended: A first (MVP), design the GML/Python protocol so B can replace the transport later.** Rationale: lowest risk, matches Undertale precedent, works on Proton without DLLs.

### Tasks
- [ ] Define file protocol (in the game's save dir): `ap_out.txt` (game->client: location checked ids, goal, death, heartbeat), `ap_in.txt` (client->game: received items w/ index, deathlink, slot info). Use append-only line format + atomic write (write tmp + rename) [U: file_rename availability in GMS1 - verify]; game acknowledges by index.
- [ ] GML patch objects/scripts: `ap_init`, `ap_poll` (Step/alarm every N frames), `ap_send_location(id)`, `ap_receive_item(id)`, `ap_on_goal`, `ap_on_death`, optional on-screen message queue (reuse game's text box).
- [ ] Hook the central item-give function: if location is AP-randomized, suppress vanilla item, mark location checked, send id; show "found X for Player".
- [ ] Persist AP state per save slot (received_index, checked locations) in the game's save or sidecar file keyed by seed+slot name, to survive reloads.
- [ ] Patch script (UndertaleModCli `--load data.win --scripts ApPatch.csx --output data.win`) [U exact flags: check `--help`], idempotent, verifies original checksum before patching.
- [ ] Python client: CommonContext subclass (`game="Devil Spire"`, tags AP/DeathLink), connect, parse slot_data, `ReceivedItems` -> write ap_in, watch ap_out -> `LocationChecks`/`StatusUpdate`; DeathLink via Bounce; reconnect handling; resend unsent checks on reconnect (use `ctx.checked_locations` diff).
- [ ] Register client as Launcher component (`components.append(Component("Devil Spire Client", ...))`) [U exact API; copy Undertale's `launch_client`].
- [ ] Locate game save dir automatically (settings entry in host.yaml for Proton path).
- [ ] DeathLink: send on player death (with cause), receive -> kill player safely (not during cutscene/menu); grace timer to avoid loops.
- [ ] Proton: provide Linux launch notes (Steam launch option or wrapper to run client alongside); confirm game reads patched data.win placed in install dir (or run patched copy as non-Steam game) .
- [ ] (Later) Transport B: try raw TCP to 127.0.0.1 from GML; if it works under Proton, add as optional mode.

## Phase 5 - Packaging / distribution
- [ ] `devilspire.apworld` (Build APWorlds) with archipelago.json (game, world_version, minimum_ap_version = current stable AP at time of release [U], authors).
- [ ] Patcher: a standalone script/CLI (`apply_patch.py`) that takes the user's own data.win, verifies hash, shells to UndertaleModCli (or bundles a binary patch/xdelta of changes only) [U: pick one; prefer script so no game bytes are redistributed].
- [ ] Optionally implement as AP `APPatch`/`APContainer` subclass (worlds/Files.py) so generate_output produces a per-slot patch file [U: confirm API].
- [ ] Setup guide for Windows, Linux native, and Steam Proton/NixOS (flake snippet).
- [ ] README with credits, license, how to report bugs; GitHub releases with apworld + patch + client.
- [ ] (Optional) PR to Archipelago core / apworld index / "Supported Games" listing; follow their new-game requirements [U: check docs on current process].

## Phase 6 - Testing
- [ ] Unit tests (apworld logic, options, every location reachable in all-options-on seed; `test.general` suite passes).
- [ ] Generate solo seeds with `Generate.py`; confirm spoiler matches expectations; run with `--skip_output` style fuzz for options.
- [ ] Offline protocol test: fake game dir + client against a local `MultiServer.py` (no game) - verify items/locations round trip.
- [ ] In-game manual test checklist: each location type, each item type, receive while in menu/cutscene, save/reload dupes, death/DeathLink, goal, disconnect/reconnect, two-game multiworld with e.g. a trivially simple game (Archipelago "Manual"/ClientServer sample) [U].
- [ ] Soft-lock review (key items obtainable, one-way doors, missable items).
- [ ] Regression: unpatched game still launches; patch idempotency; Steam update changes hash -> clear error.
- [ ] Proton specific: different Proton versions (GE vs Valve), path discovery, file timing.
- [ ] Playtest group, collect logs; add in-client `/debug` command and log file.

## Open questions for the user
1. Should the patched game be a copy (non-Steam shortcut) or replace data.win in the Steam install (Steam updates may overwrite)?
2. Which locations do you want checks on first (chests only, bosses, NPC quests, shop items, level ups)? Is there an existing item/chest list or wiki?
3. Goal: kill final boss / reach a specific ending? Multiple endings?
4. Does the game have classes/characters/difficulty modes that affect logic?
5. Scope: personal/private project or planning to submit to the AP community (affects licensing, docs, tests rigor)?
6. Is the game's developer OK with a mod (any modding policy or Discord)?
7. Are you ok with a Python client running next to the game (native Linux) rather than inside the Proton prefix?
8. Do you have Windows access for GUI UndertaleModTool if CLI is insufficient?
9. Preferred AP version to target (latest stable vs main)?
10. DeathLink wanted? Traps wanted?

## Decisions (2026-10-11)
- Patched game is a separate copy (still requires the original game); distributed as a patch, never the game files.
- First checks: bosses.
- Goal: beat Descent (100 floors); Descent is locked by default, so unlock it from the start.
- Fan-made, unofficial community project.
- DeathLink: yes.

## Roguelike-loop design (2026-10-11)
- Slay-the-Spire-like: death resets the Descent save; ALL received AP items are re-granted on each new run (client/patch must re-apply the full received list on every new save); boss checks persist across runs; items are persistent unlocks.
- Locations (2026-10-11): every Descent floor -1..-100 is a check ("Reach Floor -N", option `floor_checks`: every floor [default] / every 5th / every 10th / off), separate from boss checks; Golems = ONE boss check; -99 gauntlet is both. Filler/souls/orbs are re-granted on every new run like all other items.
- Skeleton apworld: worlds-src/devilspire (placeholder IDs base 7_470_000; 10 boss locations incl. -99 gauntlet, Rhamdon event = Victory; depth keys gate 10-floor tiers).
