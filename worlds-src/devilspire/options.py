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
    Granularity of "Reach Floor -N" location checks (separate from boss, locked chest and shop checks).
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


class Difficulty(Choice):
    """
    Game difficulty for every Archipelago (Descent) run. The game locks it: the title's difficulty selector shows it
    and can't change it. Extreme and Nightmare don't need to be unlocked.
    """
    display_name = "Difficulty"
    option_easy = 0
    option_normal = 1
    option_hard = 2
    option_extreme = 3
    option_nightmare = 4
    default = 3


@dataclass
class DevilSpireOptions(PerGameCommonOptions):
    death_link: DeathLink
    trap_percentage: TrapPercentage
    floor_checks: FloorChecks
    difficulty: Difficulty


option_groups = [
    OptionGroup("Locations", [FloorChecks]),
    OptionGroup("Extras", [Difficulty, DeathLink, TrapPercentage]),
]
