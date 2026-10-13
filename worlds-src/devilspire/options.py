from dataclasses import dataclass

from Options import Choice, DeathLink, OptionGroup, PerGameCommonOptions, Range, Toggle


class TrapPercentage(Range):
    """
    Percentage of filler items replaced by traps (Ambush: enemies spawn around you, Plague: random ailments,
    Pickpocket: lose half your carried gold). Traps fire once when received while playing and are NOT re-applied
    on later runs.
    """
    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 0


class FloorChecks(Choice):
    """
    Granularity of "Reach Floor -N" location checks (separate from boss, chest and shop checks).
    Every 2nd (default): floors -1, -3, ..., -99 (50 checks). Every Floor: all 100 floors. Every 5th / Every 10th:
    -1, -6, ..., -96 / -1, -11, ..., -91. Off: no floor checks.
    Every floor and boss is reachable from the start (no key gating).
    Checks persist across runs; your received items are re-granted on every new run.
    """
    display_name = "Floor Checks"
    option_every_floor = 0
    option_every_5th = 1
    option_every_10th = 2
    option_off = 3
    option_every_2nd = 4
    default = 4

    @property
    def step(self) -> int:
        return {0: 1, 1: 5, 2: 10, 3: 0, 4: 2}[self.value]


class ChestChecks(Range):
    """
    Chest checks per 10-floor band (floors -1 to -10, -11 to -20, ...). Opening chests in the tower sends them, at most
    this many per band, so every depth has to be explored. Mimics don't count. 0 = off.
    """
    display_name = "Chest Checks"
    range_start = 0
    range_end = 5
    default = 3


@dataclass
class DevilSpireOptions(PerGameCommonOptions):
    death_link: DeathLink
    trap_percentage: TrapPercentage
    floor_checks: FloorChecks
    chest_checks: ChestChecks


option_groups = [
    OptionGroup("Locations", [FloorChecks, ChestChecks]),
    OptionGroup("Extras", [DeathLink, TrapPercentage]),
]
