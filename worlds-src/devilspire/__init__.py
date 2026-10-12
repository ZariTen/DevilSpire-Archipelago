from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld, World

from . import items, locations, regions, rules
from . import options as ds_options
from .constants import BASE_ID, GAME_NAME


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
    resets, but everything you have received (including filler) is re-granted on the next run. (Unofficial; not affiliated with the developer.)
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

    def _starting_keys(self) -> list[str]:
        n = self.options.starting_depth.value
        mode = self.options.floor_key_mode
        if n == 0 or mode == mode.option_off:
            return []
        if mode == mode.option_progressive:
            return [items.PROGRESSIVE_KEY] * n
        return items.KEY_NAMES[:n]

    def generate_early(self) -> None:
        for name in self._starting_keys():
            self.multiworld.push_precollected(self.create_item(name))

    def create_regions(self) -> None:
        regions.create_regions(self)

    def set_rules(self) -> None:
        rules.set_rules(self)

    def create_items(self) -> None:
        mode = self.options.floor_key_mode
        pool: list[str] = []
        if mode == mode.option_progressive:
            pool += [items.PROGRESSIVE_KEY] * (len(items.KEY_NAMES) - self.options.starting_depth.value)
        elif mode == mode.option_individual:
            pool += items.KEY_NAMES[self.options.starting_depth.value:]

        n_locations = len(self.multiworld.get_unfilled_locations(self.player))
        while len(pool) < n_locations:
            if self.random.randrange(100) < self.options.trap_percentage.value:
                pool.append(self.random.choice(items.TRAP_NAMES))
            else:
                pool.append(self.get_filler_item_name())
        self.multiworld.itempool += [self.create_item(n) for n in pool]

    def create_item(self, name: str) -> items.DevilSpireItem:
        return items.DevilSpireItem(name, items.ITEM_TABLE[name].classification,
                                    items.ITEM_NAME_TO_ID[name], self.player)

    def get_filler_item_name(self) -> str:
        return self.random.choice(items.FILLER_NAMES)

    def fill_slot_data(self) -> Mapping[str, Any]:
        return {
            **self.options.as_dict("death_link", "floor_key_mode", "starting_depth", "floor_checks"),
            "goal": "descent_rhamdon",  # fixed
            "descent_unlocked": True,  # patch force-unlocks Descent
            "persistent_items": True,  # client must re-apply ALL received items on every new Descent save
            "base_id": BASE_ID,
        }
