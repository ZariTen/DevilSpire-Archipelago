# Host guide (fan-made, unofficial)

## 1. Requirements
- Archipelago **0.6.8 or newer** (host and every player of this game).
- `devilspire.apworld` from the GitHub Releases page. Current apworld `world_version`: **0.1.0**. Use the same release for host and players (the apworld contains the world, the client and the game patch); tell your players the version.

## 2. Install the world
- Double-click `devilspire.apworld` (Archipelago must be installed), **or** copy it into the `custom_worlds` folder of your Archipelago install, **or** (source install) put the `devilspire` folder in `worlds/`. Restart the Launcher.
- Check: Launcher > *Generate Template Options* now contains `Devil Spire.yaml`.

## 3. The options file
Start from [examples/DevilSpire.yaml](../examples/DevilSpire.yaml) or the generated template. Set `name:` (the slot name; players need it) and `game: Devil Spire`. Options:
- `death_link` (true/false): dying in one DeathLink game kills everyone else with DeathLink on, and vice versa.
- `floor_checks`: which "Reach Floor -N" locations exist, in addition to boss kills.
  `every_floor` (all 100 floors, default), `every_5th` (-1, -6, -11, ... -96), `every_10th` (-1, -11, ... -91), `off` (bosses only).
- `trap_percentage` (0-100, default 0): percent of filler items turned into traps (Ambush: enemies appear; Plague: random ailments; Pickpocket: lose half your carried gold). Traps fire once when received while playing.
- Standard Archipelago options (`progression_balancing`, `accessibility`, ...) work as usual.
Goal: beat the final Descent boss (floor -100). Every floor and boss is reachable from the start (no keys).
Items are persistent unlocks: after a death, all received items are granted again at the next camp chest.

## 4. Generate and host
1. Put every player's yaml into the `Players` folder of Archipelago, then Launcher > *Generate*.
2. Output is `output/AP_<seed>.zip`. Host it with the Launcher's *Host* (or `ArchipelagoServer`), or upload it to archipelago.gg's host page. Custom (non-core) worlds can only be hosted on archipelago.gg if they ship there; otherwise host it on your own machine, and forward the port (default 38281).
3. Give players: address:port, slot names, password, and the **release version** (and a link to this project's Releases page and README).

## 5. Version compatibility
- Archipelago: min 0.6.8 (`minimum_ap_version` in `archipelago.json`).
- `world_version` is in `archipelago.json`/the apworld; the client reads item/location IDs from the same apworld, so mismatched apworld versions between the generating host and a player's installed apworld can cause wrong IDs. Items/locations use base ID 38,470,000.
- The client's `/auto_patch` only supports one exact original `data.win` (sha256 `44df3801...c9b4`, see `patch/EXPECTED_ORIGINAL_SHA256`); the same patch works for every seed. The in-game patch changes only when the apworld version changes (players then run `/auto_patch` again).

## 6. Troubleshooting
- Players can't connect: server port open? correct slot name (case sensitive)? same AP version family?
- "Game not found / unknown game Devil Spire" in Generate: the apworld isn't installed on the generating machine, or the file name is not `devilspire.apworld`.
- Generation errors: run Generate from the Launcher and read the log; try `floor_checks: off` to rule out the big location set.
- Player's `/auto_patch` says hash mismatch: see [PLAYER_GUIDE.md](PLAYER_GUIDE.md) section 8.
- Player's client can't find the save folder: see [PLAYER_GUIDE.md](PLAYER_GUIDE.md) (`/savedir`, `--savedir`).
