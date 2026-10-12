from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

from . import rules
from .constants import NUM_TIERS
from .items import DevilSpireItem
from .locations import (BOSS_LOCATIONS, floor_checks_enabled, VICTORY_ITEM, VICTORY_LOCATION, DevilSpireLocation,
                        LOCATION_NAME_TO_ID)

if TYPE_CHECKING:
    from . import DevilSpireWorld


def tier_region_name(tier: int) -> str:
    return f"Descent Floors -{tier * 10 + 1} to -{tier * 10 + 10}"


def create_regions(world: DevilSpireWorld) -> None:
    mw, p = world.multiworld, world.player
    menu = Region("Menu", p, mw)
    tiers = [Region(tier_region_name(t), p, mw) for t in range(NUM_TIERS)]
    mw.regions += [menu, *tiers]

    menu.connect(tiers[0], "Start Descent")  # Descent is force-unlocked by the patch
    for t in range(1, NUM_TIERS):
        # Menu -> tier 0 is open; deeper tiers chain on the previous one. Key rule per tier (see rules.py).
        tiers[t - 1].connect(tiers[t], f"Descend to tier {t}", rules.tier_rule(world, t))

    locs = list(BOSS_LOCATIONS) + floor_checks_enabled(world.options.floor_checks.step)
    for d in locs:
        tiers[d.tier].locations.append(
            DevilSpireLocation(p, d.name, LOCATION_NAME_TO_ID[d.name], tiers[d.tier]))

    # Goal: Rhamdon on floor -100 (last tier). Event location + "Victory" event item.
    tiers[NUM_TIERS - 1].add_event(VICTORY_LOCATION, VICTORY_ITEM,
                                   location_type=DevilSpireLocation, item_type=DevilSpireItem)
