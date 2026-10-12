"""Items: power boosts. NOTHING gates progression (Slay-the-Spire style): all floors/bosses are reachable from the start.

Received items persist across deaths: the patch re-applies the FULL received list at the start of every new run
(stat orbs stack, consumables/gold/souls are re-granted each run - accepted behaviour). Ids/effects: docs/item-catalog.md.
Item id = BASE_ID + ITEM_OFFSET + code.
"""
from __future__ import annotations

from typing import NamedTuple

from BaseClasses import Item, ItemClassification

from .constants import BASE_ID, ITEM_OFFSET

U, F, T = ItemClassification.useful, ItemClassification.filler, ItemClassification.trap


class DevilSpireItem(Item):
    game = "Devil Spire"


class ItemData(NamedTuple):
    code: int  # relative id (patch: rel = item_id - base_id - 500)
    classification: ItemClassification
    count: int  # copies in the default 110-item pool
    group: str


_ITEMS: list[tuple[str, int, ItemClassification, int, str]] = [
    # stat boosts (game's red-orb effect: +3 to one stat, applied to the live player; stat-specific)
    ("Orb of Strength", 100, U, 4, "Stat Boosts"),
    ("Orb of Intelligence", 101, U, 4, "Stat Boosts"),
    ("Orb of Vitality", 102, U, 6, "Stat Boosts"),
    ("Orb of Agility", 103, U, 4, "Stat Boosts"),
    ("Stat Point", 104, U, 4, "Stat Boosts"),  # +1 unspent point (level-up currency, spent in the character sheet)
    # gold / stones / souls
    ("Yellow Orb (Gold)", 110, F, 14, "Gold"),  # 150-450 gold (like the boss yellow orb)
    ("Gold Hoard", 111, F, 4, "Gold"),  # 1000 gold
    ("Blue Orb (Stone)", 112, F, 10, "Stones"),  # random Stone item (36 kinds), apply to equipment manually
    ("Pouch of Souls", 113, F, 8, "Souls"),  # +100 souls (meta currency)
    # consumables
    ("Red Potion Pack", 120, F, 8, "Consumables"),  # 3x Red Potion (full HP)
    ("Blue Potion Pack", 121, F, 4, "Consumables"),  # 3x Blue Potion (full MP)
    ("White Potion", 122, F, 3, "Consumables"),  # 1x White Potion (full heal + cure)
    # grimoire pages (random spell of a tier, never a duplicate of a known spell)
    ("Spell Page (Basic)", 130, F, 4, "Spells"),  # spell types 0-11
    ("Spell Page (Advanced)", 131, F, 3, "Spells"),  # 12-23
    ("Spell Page (Master)", 132, U, 2, "Spells"),  # 24-47
    # equipment: random item of the category at "level" L (stats scale ~linearly with L, see catalog)
    ("Weapon (Lv 25)", 140, F, 3, "Equipment"),
    ("Weapon (Lv 50)", 141, U, 3, "Equipment"),
    ("Weapon (Lv 75)", 142, U, 2, "Equipment"),
    ("Armor Piece (Lv 25)", 143, F, 3, "Equipment"),
    ("Armor Piece (Lv 50)", 144, U, 3, "Equipment"),
    ("Armor Piece (Lv 75)", 145, U, 3, "Equipment"),
    ("Accessory (Lv 25)", 146, F, 2, "Equipment"),
    ("Accessory (Lv 50)", 147, U, 2, "Equipment"),
    ("Accessory (Lv 75)", 148, U, 1, "Equipment"),
    ("Shield (Lv 25)", 149, F, 1, "Equipment"),
    ("Shield (Lv 50)", 150, U, 2, "Equipment"),
    ("Mystic Ring", 151, F, 3, "Equipment"),  # random ring (36 kinds, the stone-effect rings)
    # traps (count 0 in the template: only created through trap_percentage, replacing filler). Fire ONCE when received live.
    ("Ambush Trap", 200, T, 0, "Traps"),  # 3-5 floor-appropriate enemies spawn around the player
    ("Plague Trap", 201, T, 0, "Traps"),  # random body+mind ailments
    ("Pickpocket Trap", 202, T, 0, "Traps"),  # lose half of carried gold
]

ITEM_TABLE: dict[str, ItemData] = {n: ItemData(c, k, cnt, g) for n, c, k, cnt, g in _ITEMS}
ITEM_NAME_TO_ID: dict[str, int] = {n: BASE_ID + ITEM_OFFSET + d.code for n, d in ITEM_TABLE.items()}

FILLER_NAMES = [n for n, d in ITEM_TABLE.items() if d.classification == F]
TRAP_NAMES = [n for n, d in ITEM_TABLE.items() if d.classification == T]

# the default-size pool template (sums to 110 = locations with floor_checks every_floor)
POOL_TEMPLATE: list[str] = [n for n, d in ITEM_TABLE.items() for _ in range(d.count)]

ITEM_NAME_GROUPS: dict[str, set[str]] = {}
for _n, _d in ITEM_TABLE.items():
    ITEM_NAME_GROUPS.setdefault(_d.group, set()).add(_n)
