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


class FloorMilestones(Toggle):
    """
    STUB: adds a "Reach Floor -N" location at every 10 floors (-5, -15, ... -95). Disabled by default.
    Not yet implemented in the patch.
    """
    display_name = "Floor Milestone Locations"


@dataclass
class DevilSpireOptions(PerGameCommonOptions):
    death_link: DeathLink
    floor_key_mode: FloorKeyMode
    starting_depth: StartingDepth
    trap_percentage: TrapPercentage
    floor_milestones: FloorMilestones


option_groups = [
    OptionGroup("Progression", [FloorKeyMode, StartingDepth]),
    OptionGroup("Extras", [DeathLink, TrapPercentage, FloorMilestones]),
]
