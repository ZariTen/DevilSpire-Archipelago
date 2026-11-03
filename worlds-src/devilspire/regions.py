from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import LocationProgressType, Region

from .constants import NUM_TIERS
from .items import DevilSpireItem
from .locations import (BOSS_LOCATIONS, floor_checks_enabled, LOCKED_LOCATIONS, SHOP_LOCATIONS, VICTORY_ITEM, VICTORY_LOCATION, DevilSpireLocation,
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

    # Chain Menu -> tier 0 -> tier 1 -> ... -> tier 9. Gear rules on the entrances: rules.GEAR_REQUIRED.
    menu.connect(tiers[0], "Descend to tier 0")
    for t in range(1, NUM_TIERS):
        tiers[t - 1].connect(tiers[t], f"Descend to tier {t}")

    locs = (list(BOSS_LOCATIONS) + floor_checks_enabled(world.options.floor_checks.step)
            + list(LOCKED_LOCATIONS) + list(SHOP_LOCATIONS))
    # Bosses up to Snake (-59) and shop stands always hold a progression item. Apparition and deeper are left out:
    # they need near-max gear, and as priority spots they made 0.3-20% of solo fills fail (FillError).
    # Set at creation, so core's exclude_locations (applied after set_rules) still overrides it.
    priority = {d.name for d in BOSS_LOCATIONS if d.tier <= 5} | {d.name for d in SHOP_LOCATIONS}
    for d in locs:
        loc = DevilSpireLocation(p, d.name, LOCATION_NAME_TO_ID[d.name], tiers[d.tier])
        if d.name in priority and loc.progress_type == LocationProgressType.DEFAULT:
            loc.progress_type = LocationProgressType.PRIORITY
        tiers[d.tier].locations.append(loc)

    # Goal: Rhamdon on floor -100 (last tier). Event location + "Victory" event item.
    tiers[NUM_TIERS - 1].add_event(VICTORY_LOCATION, VICTORY_ITEM,
                                   location_type=DevilSpireLocation, item_type=DevilSpireItem)
