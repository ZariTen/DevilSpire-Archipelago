from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import Component, Type, components, launch as launch_component

from . import items, locations, regions, rules
from . import options as ds_options
from .constants import BASE_ID, GAME_NAME


def launch_client(*args: str) -> None:
    from .ds_client import launch  # lazy: pulls in CommonClient
    launch_component(launch, name="DevilSpireClient", args=args)


components.append(Component("Devil Spire Client", func=launch_client, component_type=Type.CLIENT,
                            game_name=GAME_NAME, supports_uri=True))


class DevilSpireWebWorld(WebWorld):
    game = GAME_NAME
    theme = "dirt"
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Devil Spire (fan-made Archipelago integration) for MultiWorld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Zari Ten"],
    )
    tutorials = [setup_en]
    option_groups = ds_options.option_groups


class DevilSpireWorld(World):
    """
    Devil Spire is a roguelike dungeon crawler. In this fan-made randomizer you descend 100 floors of the
    Descent, defeat the bosses guarding every tenth floor, and finally slay Rhamdon. When you die the run
    resets, but everything you have received (stat boosts, equipment, gold, ...) is re-granted on the next run. All floors are open from the start. (Unofficial; not affiliated with the developer.)
    """

    game = GAME_NAME
    web = DevilSpireWebWorld()

    options_dataclass = ds_options.DevilSpireOptions
    options: ds_options.DevilSpireOptions

    item_name_to_id = items.ITEM_NAME_TO_ID
    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_groups = items.ITEM_NAME_GROUPS
    location_name_groups = locations.LOCATION_NAME_GROUPS

    origin_region_name = "Menu"
    topology_present = False

    def create_regions(self) -> None:
        regions.create_regions(self)

    def set_rules(self) -> None:
        rules.set_rules(self)

    def create_items(self) -> None:
        n_locations = len(self.multiworld.get_unfilled_locations(self.player))
        pool = list(items.POOL_TEMPLATE)  # 110 entries = default location count
        if n_locations < len(pool):
            self.random.shuffle(pool)
            pool = pool[:n_locations]  # random subset (no logic depends on items)
        while len(pool) < n_locations:
            pool.append(self.get_filler_item_name())
        # traps replace filler entries with trap_percentage
        pct = self.options.trap_percentage.value
        if pct:
            for i, name in enumerate(pool):
                if items.ITEM_TABLE[name].classification == items.F and self.random.randrange(100) < pct:
                    pool[i] = self.random.choice(items.TRAP_NAMES)
        self.multiworld.itempool += [self.create_item(n) for n in pool]

    def create_item(self, name: str) -> items.DevilSpireItem:
        return items.DevilSpireItem(name, items.ITEM_TABLE[name].classification,
                                    items.ITEM_NAME_TO_ID[name], self.player)

    def get_filler_item_name(self) -> str:
        return self.random.choice(items.FILLER_NAMES)

    def fill_slot_data(self) -> Mapping[str, Any]:
        return {
            **self.options.as_dict("death_link", "floor_checks", "trap_percentage"),
            "goal": "descent_rhamdon",  # fixed
            "descent_unlocked": True,  # patch force-unlocks Descent
            "gating": False,  # no depth keys: everything reachable from the start
            "persistent_items": True,  # client must re-apply ALL received items on every new Descent save
            "base_id": BASE_ID,
        }
