# Host guide

Only you and the Devil Spire players need `devilspire.apworld`. Players of other games don't.

## Steps
1. Install Archipelago 0.6.8 or newer.
2. Double-click `devilspire.apworld`. (Or copy it into `custom_worlds`.) Restart the Launcher.
3. Copy [examples/DevilSpire.yaml](../examples/DevilSpire.yaml). Set `name:` to the player's slot name.
4. Put all player YAML files in Archipelago's `Players` folder.
5. In the Launcher, click *Generate*. Then host the `.zip` from the `output` folder.
6. Send players the address, slot names, password, and the apworld version you used.

Use the same apworld version as your Devil Spire players.

## Options
| Option | Values | Meaning |
|---|---|---|
| `death_link` | true / false | Deaths are shared with other DeathLink players. |
| `floor_checks` | `every_floor` (default), `every_5th`, `every_10th`, `off` | Which floors count as checks. Bosses always count. |
| `trap_percentage` | 0-100 (default 0) | Share of filler items that become traps. |

The goal is beating the boss on floor -100. Nothing is locked: every floor can be reached from the start.

## Problems
- **"Unknown game Devil Spire" when generating:** the apworld isn't installed on this computer.
- **Players can't connect:** check the port is open and the slot name is exact (case matters).
- Player-side problems: see the [Player guide](PLAYER_GUIDE.md#problems).
