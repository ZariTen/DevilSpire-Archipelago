from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import NUM_TIERS
from .locations import VICTORY_ITEM

if TYPE_CHECKING:
    from . import DevilSpireWorld

# Depth logic: copies of Progressive Weapon AND Progressive Armor (n of each) expected before floor tier t
# (floors -10t-1 .. -10t-10). Floors -1..-20 are free; floors -91..-100 (Rhamdon) need 6 + 6 (7 of each in the pool).
# Logic only: the game itself locks no floor.
GEAR_REQUIRED = [0, 0, 1, 2, 2, 3, 4, 4, 5, 6]
assert len(GEAR_REQUIRED) == NUM_TIERS


def set_rules(world: DevilSpireWorld) -> None:
    p = world.player
    for t, n in enumerate(GEAR_REQUIRED):
        if n:
            world.get_entrance(f"Descend to tier {t}").access_rule = \
                lambda state, n=n: state.has_all_counts({"Progressive Weapon": n, "Progressive Armor": n}, p)
    world.multiworld.completion_condition[world.player] = lambda state: state.has(VICTORY_ITEM, world.player)
