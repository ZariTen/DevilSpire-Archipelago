from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import GAME_NAME
from .locations import VICTORY_ITEM

if TYPE_CHECKING:
    from . import DevilSpireWorld

# No key / item rules: every floor and boss is reachable from the start (items are only power boosts), so the
# multiworld is always completable without outside items. Only the goal (Rhamdon) event remains.


def set_rules(world: DevilSpireWorld) -> None:
    world.multiworld.completion_condition[world.player] = lambda state: state.has(VICTORY_ITEM, world.player)
