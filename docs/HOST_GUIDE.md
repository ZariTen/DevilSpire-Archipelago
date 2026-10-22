# Host guide

Only you and the Devil Spire players need `devilspire.apworld`. Players of other games don't.

## Steps
1. Install Archipelago 0.6.8 or newer.
2. Double-click `devilspire.apworld` (or copy it into `custom_worlds`). Restart the Launcher.
3. Copy [examples/DevilSpire.yaml](../examples/DevilSpire.yaml) and set `name:` to the player's slot name.
4. Put all player yaml files in Archipelago's `Players` folder.
5. In the Launcher, click *Generate*. Host the `.zip` from the `output` folder.
6. Send players the address, slot names, password, and the apworld version you used.

Use the same apworld version as your Devil Spire players.

## Options
| Option | Values | Meaning |
|---|---|---|
| `floor_checks` | `every_2nd` (default), `every_floor`, `every_5th`, `every_10th`, `off` | Which floors are checks. |
| `difficulty` | `easy`, `normal`, `hard`, `extreme` (default), `nightmare` | Game difficulty. Locked in game. |
| `death_link` | `true` / `false` | Deaths are shared with other DeathLink players. |
| `trap_percentage` | 0-100 (default 0) | Share of filler items that become traps. |

## Checks
| Check | Count |
|---|---|
| Bosses (floors -9, -19, ... -99) | 10 |
| Floors (`floor_checks`) | 50 with `every_2nd` (100 / 20 / 10 / 0 for the others) |
| Locked chest, one per floor (not boss or shop floors) | 80 |
| Shop items on floors -10 to -90 (2 each) | 18 |

Default total: 158. The goal is beating the boss on floor -100. Nothing is locked: no item gates any floor.
Items: see the [item catalog](dev/item-catalog.md).

## Problems
- **"Unknown game Devil Spire" when generating:** the apworld isn't installed on this computer.
- **Players can't connect:** check the port is open and the slot name is exact (case matters).
- Player problems: see the [Player guide](PLAYER_GUIDE.md#7-problems).
