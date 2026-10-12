"""Items. ALL names/IDs are PLACEHOLDER pending reverse-engineering of the real item scripts.

Items are PERSISTENT unlocks: the client/patch must re-apply the full received-items list at the start of every
new Descent run (the Descent save is wiped on death). Therefore no item here is a one-shot 'consumed' effect in
logic terms; filler like souls/orbs is re-granted per run by the patch, or granted once to the persistent
souls.ini - to be decided (see docs/en_Devil Spire.md).
"""
from __future__ import annotations

from typing import NamedTuple

from BaseClasses import Item, ItemClassification

from .constants import BASE_ID, ITEM_OFFSET, NUM_TIERS


class DevilSpireItem(Item):
    game = "Devil Spire"


class ItemData(NamedTuple):
    code: int  # relative id
    classification: ItemClassification


PROGRESSIVE_KEY = "Progressive Depth Key"


def key_name(tier: int) -> str:
    """Individual key opening tier `tier` (1..9)."""
    lo = tier * 10 + 1
    return f"Depth Key {tier} (Floors -{lo} to -{lo + 9})"


KEY_NAMES = [key_name(t) for t in range(1, NUM_TIERS)]  # tier 0 needs no key

FILLER_NAMES = ["Pouch of Souls", "Red Orb", "Yellow Orb", "Blue Orb"]  # placeholder; orbs: see research notes
TRAP_NAMES = ["Weakness Trap", "Monster Swarm Trap"]

ITEM_TABLE: dict[str, ItemData] = {
    PROGRESSIVE_KEY: ItemData(0, ItemClassification.progression),
    **{n: ItemData(1 + i, ItemClassification.progression) for i, n in enumerate(KEY_NAMES)},
    # 100+: filler, 200+: traps (relative to ITEM_OFFSET)
    **{n: ItemData(100 + i, ItemClassification.filler) for i, n in enumerate(FILLER_NAMES)},
    **{n: ItemData(200 + i, ItemClassification.trap) for i, n in enumerate(TRAP_NAMES)},
}

ITEM_NAME_TO_ID: dict[str, int] = {n: BASE_ID + ITEM_OFFSET + d.code for n, d in ITEM_TABLE.items()}

ITEM_NAME_GROUPS: dict[str, set[str]] = {
    "Depth Keys": {PROGRESSIVE_KEY, *KEY_NAMES},
    "Filler": set(FILLER_NAMES),
    "Traps": set(TRAP_NAMES),
}
