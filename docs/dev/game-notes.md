# Game notes

Facts about Devil Spire v1.5999 (GameMaker Studio 1) that the patch relies on, found by reading the decompiled code
locally (`game-copy/dump/`, git-ignored). Object and script names are the game's own; line numbers are approximate.

## Modes and floors
- `global.mode`: 0 Ascent, 1 Descent, 2 Chaos, 3 Arena, 4 Immortal, 5 Soul. We use Descent only.
- Descent floors are negative: `global.level` -1 .. -100 (`next_floor` decrements, skipping 0; camp floors are 0, 0.4, 0.5).
- Dungeon theme = `floor((-level - 1) / 10)` (`get_dungeon`): 10 themes x 10 floors.
- Difficulty `global.difficulty` 0..4; Extreme and Nightmare need `global.extreme` / `global.nightmare` (the patch unlocks them).
- Descent unlock: `global.descent`, read from `unlocks.ini` in `obj_setup_Alarm_0`; normally bought for 1000 souls.
  The patch sets it to 1 (no achievement).

## Bosses
- Boss floor in Descent: `abs(level) % 10 == 9`, or level -100 (`obj_floor` Create). Spawned in `obj_dungeoncreator_Step_0`.
- Bosses only spawn if the player has a kill on this run (`global.kills > 0`); otherwise the room is empty.

| Floor | Boss object |
|---|---|
| -9 | obj_slime |
| -19 | obj_abomination |
| -29 | obj_idol |
| -39 | obj_golem x2 (one check) |
| -49 | obj_dragon |
| -59 | obj_snake |
| -69 | obj_apparition |
| -79 | obj_girl |
| -89 | obj_robot |
| -99 | no boss object: 15 normal enemies ("gauntlet") |
| -100 | obj_rhamdon (goal) |

- Boss-cleared hook: in `obj_enemy_Step_0`, the boss-floor branch that runs once when the last living enemy dies
  (covers both golems, the gauntlet and Rhamdon). No per-boss flag is saved, so the patch reports it at once.
- Goal hook: `obj_rhamdon_Step_1`, right before it switches to `rom_ending`. The ending deletes the Descent save.

## Saves
- All files are relative names (`ini_open` etc.) in `%APPDATA%\<GEN8 Name>`; the patch renames it to `Devil_Spire_AP`.
- Files: `config.ini`, `unlocks.ini`, `souls.ini` (anti-tamper check), `<mode>_character.ini`, `corpse.ini`, `tombstone<N>.ini`.
- `save_game(mode)` runs only at character creation and on every floor change. No manual save.
- Loading a save schedules its deletion (`obj_god` alarm), rewritten at the next floor: quitting mid-floor loses that floor.
- Descent is permadeath: on death the character file is copied to `corpse.ini` and deleted.

## Death
- `obj_player_Step_0`: `hp == 0` starts the death; after the countdown, a revive enchantment (10) may save the player,
  otherwise `game_over` (adds souls, goes to `rom_gameover`). DeathLink send hooks the real death.
- DeathLink receive sets the player's hp to 0, only inside the tower.

## Items
- `generate_*` scripts create an item instance; `get_item` (as obj_player) adds it with `add_inventory` (100 slots,
  weight cap) or `add_grimoire` (24 spells). Details and formulas: [item-catalog.md](item-catalog.md).
- Orbs (`obj_orb`, handled in `interact`): red = +3 to a stat, yellow = gold, blue = stone. Each boss floor drops one of each.
- `obj_god` is a persistent per-frame object: the patch polls the save folder from its Step event.
