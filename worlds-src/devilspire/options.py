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
    Granularity of "Reach Floor -N" location checks (separate from boss kill checks).
    Every Floor: all 100 Descent floors (-1 to -100) are checks. Every 5th / Every 10th: only floors that are a
    counted from floor -1 (every 5th: -1, -6, -11, ..., -96; every 10th: -1, -11, ..., -91; floor -100 is the goal
    fight, not a floor check, unless every floor is on). Off: no floor checks (bosses only).
    Every floor and boss is reachable from the start (no key gating).
    Checks persist across runs; your received items are re-granted on every new run.
    """
    display_name = "Floor Checks"
    option_every_floor = 0
    option_every_5th = 1
    option_every_10th = 2
    option_off = 3
    default = 0

    @property
    def step(self) -> int:
        return {0: 1, 1: 5, 2: 10, 3: 0}[self.value]


@dataclass
class DevilSpireOptions(PerGameCommonOptions):
    death_link: DeathLink
    trap_percentage: TrapPercentage
    floor_checks: FloorChecks


option_groups = [
    OptionGroup("Locations", [FloorChecks]),
    OptionGroup("Extras", [DeathLink, TrapPercentage]),
]
