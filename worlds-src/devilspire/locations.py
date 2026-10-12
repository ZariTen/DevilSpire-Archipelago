"""Locations. Names/IDs are PLACEHOLDER pending reverse-engineering (see docs/locations-bosses.md in repo root).

Boss kill checks persist across runs (Slay-the-Spire-like loop): once sent, a boss check stays checked in the
client/AP server even though the Descent save is wiped on death.
"""
from __future__ import annotations

from typing import NamedTuple

from BaseClasses import Location

from .constants import BASE_ID, LOCATION_OFFSET, MILESTONE_OFFSET


class DevilSpireLocation(Location):
    game = "Devil Spire"


class LocationData(NamedTuple):
    name: str
    floor: int  # Descent floor (global.level), negative
    tier: int  # floor tier (0..9) the location lives in
    code: int  # relative id


# floor, boss object per docs/locations-bosses.md. -99 has no boss object (15 plain obj_enemy) -> "gauntlet".
BOSS_LOCATIONS: list[LocationData] = [
    LocationData("Slime defeated (Floor -9)", -9, 0, 0),
    LocationData("Abomination defeated (Floor -19)", -19, 1, 1),
    LocationData("Idol defeated (Floor -29)", -29, 2, 2),
    LocationData("Golems defeated (Floor -39)", -39, 3, 3),  # two obj_golem, last kill counts
    LocationData("Dragon defeated (Floor -49)", -49, 4, 4),
    LocationData("Snake defeated (Floor -59)", -59, 5, 5),
    LocationData("Apparition defeated (Floor -69)", -69, 6, 6),
    LocationData("Girl defeated (Floor -79)", -79, 7, 7),
    LocationData("Robot defeated (Floor -89)", -89, 8, 8),
    LocationData("Gauntlet cleared (Floor -99)", -99, 9, 9),  # 15 plain enemies, no boss object
]

# STUB (disabled by default, option `floor_milestones`): "Reach Floor -N" for N = 5, 15, ..., 95
MILESTONE_LOCATIONS: list[LocationData] = [
    LocationData(f"Reach Floor -{t * 10 + 5}", -(t * 10 + 5), t, t) for t in range(10)
]

VICTORY_LOCATION = "Rhamdon defeated"  # event location (no id), holds the "Victory" event item
VICTORY_ITEM = "Victory"

LOCATION_NAME_TO_ID: dict[str, int] = {
    **{d.name: BASE_ID + LOCATION_OFFSET + d.code for d in BOSS_LOCATIONS},
    **{d.name: BASE_ID + MILESTONE_OFFSET + d.code for d in MILESTONE_LOCATIONS},
}

LOCATION_NAME_GROUPS: dict[str, set[str]] = {
    "Bosses": {d.name for d in BOSS_LOCATIONS},
    "Floor Milestones": {d.name for d in MILESTONE_LOCATIONS},
}
