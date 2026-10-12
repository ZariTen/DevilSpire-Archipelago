from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from BaseClasses import CollectionState

from .constants import GAME_NAME
from .items import PROGRESSIVE_KEY, key_name
from .locations import VICTORY_ITEM

if TYPE_CHECKING:
    from . import DevilSpireWorld

# Cross-run note: received items persist across runs (re-granted on every new Descent save), and boss checks
# persist, so logic is plain monotone 'has items' logic - it never has to model a single run's survival.
# (Each run is assumed capable of reaching any unlocked tier; surviving is the player's job.)


# Floor N (1..100) is reachable iff its tier ((N-1)//10) is: tier 0 free, tier t needs t progressive keys / key t
# (and, by chaining the tier regions, all shallower keys). Boss checks share their floor's tier; the Golems are a
# single check; -99 gauntlet is both a boss-type check and a floor check. -100 floor check and Rhamdon: tier 9.


def tier_rule(world: DevilSpireWorld, tier: int) -> Callable[[CollectionState], bool] | None:
    p = world.player
    mode = world.options.floor_key_mode
    if mode == world.options.floor_key_mode.option_progressive:
        return lambda state: state.has(PROGRESSIVE_KEY, p, tier)
    if mode == world.options.floor_key_mode.option_individual:
        name = key_name(tier)
        return lambda state: state.has(name, p)
    return None


def set_rules(world: DevilSpireWorld) -> None:
    world.multiworld.completion_condition[world.player] = lambda state: state.has(VICTORY_ITEM, world.player)
