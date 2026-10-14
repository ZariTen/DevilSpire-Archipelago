"""Items: power boosts. NOTHING gates progression (Slay-the-Spire style): all floors/bosses are reachable from the start.

Received items persist across deaths: the patch re-applies the received list at the start of every new run
(stat orbs stack, consumables/gold/souls are re-granted each run; progressive gear: only the best tier). Ids/effects: docs/dev/item-catalog.md.
Item id = BASE_ID + ITEM_OFFSET + code.
"""
from __future__ import annotations

from typing import NamedTuple

from BaseClasses import Item, ItemClassification

from .constants import BASE_ID, ITEM_OFFSET

U, F, T = ItemClassification.useful, ItemClassification.filler, ItemClassification.trap
P = ItemClassification.progression


class DevilSpireItem(Item):
    game = "Devil Spire"


class ItemData(NamedTuple):
    code: int  # relative id (patch: rel = item_id - base_id - 500)
    classification: ItemClassification
    count: int  # copies in the default 110-item pool
    group: str


_ITEMS: list[tuple[str, int, ItemClassification, int, str]] = [
    # stat boosts (game's red-orb effect: +3 to one stat, applied to the live player; stat-specific)
    ("Orb of Strength", 100, U, 5, "Stat Boosts"),
    ("Orb of Intelligence", 101, U, 5, "Stat Boosts"),
    ("Orb of Vitality", 102, U, 7, "Stat Boosts"),
    ("Orb of Agility", 103, U, 5, "Stat Boosts"),
    ("Stat Point", 104, U, 5, "Stat Boosts"),  # +1 unspent point (level-up currency, spent in the character sheet)
    # gold / stones / souls
    ("Yellow Orb (Gold)", 110, F, 16, "Gold"),  # 150-450 gold (like the boss yellow orb)
    ("Gold Hoard", 111, F, 4, "Gold"),  # 1000 gold
    ("Blue Orb (Stone)", 112, F, 10, "Stones"),  # random Stone item (36 kinds), apply to equipment manually
    ("Pouch of Souls", 113, F, 8, "Souls"),  # +100 souls (meta currency)
    # consumables
    ("Red Potion Pack", 120, F, 8, "Consumables"),  # 3x Red Potion (full HP)
    ("Blue Potion Pack", 121, F, 4, "Consumables"),  # 3x Blue Potion (full MP)
    ("White Potion", 122, F, 3, "Consumables"),  # 1x White Potion (full heal + cure)
    # progressive items (classification progression, but they gate NOTHING: logic stays open). The patch counts the copies
    # received so far (ap_in order): copy N gives tier N. A new run re-grants only the best gear tier (spellbook: every copy).
    ("Progressive Weapon", 160, P, 7, "Progressive"),  # copy N: random weapon at L = floor(12.5*N) (12..87)
    ("Progressive Armor", 161, P, 7, "Progressive"),  # copy N: full set (body, head, arms, legs) at L = floor(12.5*N)
    ("Progressive Shield", 162, P, 3, "Progressive"),  # copy N: shield at L = 25*N (25/50/75)
    ("Progressive Accessory", 163, P, 4, "Progressive"),  # copy N: accessory at L = 20*N (20/40/60/80)
    ("Progressive Spellbook", 164, P, 6, "Progressive"),  # copies 1-2: Basic spell, 3-4: Advanced, 5-6: Master (no duplicates)
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



def extra_items(k: int) -> list[str]:
    """k pool entries beyond the 110 template: the template's useful + filler mix scaled proportionally (largest
    remainder, deterministic). Progressive copies never grow beyond their max tier."""
    base = [n for n in POOL_TEMPLATE if ITEM_TABLE[n].classification != P]
    counts: dict[str, int] = {}
    for n in base:
        counts[n] = counts.get(n, 0) + 1
    share = {n: k * c / len(base) for n, c in counts.items()}
    out = {n: int(s) for n, s in share.items()}
    rest = k - sum(out.values())
    for n in sorted(share, key=lambda n: (-(share[n] - out[n]), list(counts).index(n)))[:rest]:
        out[n] += 1
    return [n for n in counts for _ in range(out[n])]


ITEM_NAME_GROUPS: dict[str, set[str]] = {}
for _n, _d in ITEM_TABLE.items():
    ITEM_NAME_GROUPS.setdefault(_d.group, set()).add(_n)
