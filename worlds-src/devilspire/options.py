from dataclasses import dataclass

from Options import Choice, DeathLink, OptionGroup, PerGameCommonOptions, Range, Toggle


class FloorKeyMode(Choice):
    """
    How deeper floor tiers (10 floors each) are gated.
    Progressive: 9 identical "Progressive Depth Key" items; the Nth one opens the Nth tier below floors -1..-10.
    Individual: 9 distinct keys, one per tier (tier N needs key N and all shallower tiers).
    Off: no gating; all floors are open from the start (the pool is only filler).
    Gating is enforced by the patched game: stairs below the unlocked depth refuse to open.
    """
    display_name = "Floor Key Mode"
    option_progressive = 0
    option_individual = 1
    option_off = 2
    default = 0


class StartingDepth(Range):
    """
    Number of floor tiers (10 floors each) unlocked at the start, beyond the first one (floors -1..-10),
    granted as starting keys. 0 = only the first tier.
    """
    display_name = "Starting Depth Tiers"
    range_start = 0
    range_end = 9
    default = 0


class TrapPercentage(Range):
    """Percentage of filler items replaced by traps."""
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
    Floors are reached by descending; floor N needs the depth keys of its 10-floor tier.
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
    floor_key_mode: FloorKeyMode
    starting_depth: StartingDepth
    trap_percentage: TrapPercentage
    floor_checks: FloorChecks


option_groups = [
    OptionGroup("Progression", [FloorKeyMode, StartingDepth, FloorChecks]),
    OptionGroup("Extras", [DeathLink, TrapPercentage]),
]
