"""Shared constants. EVERYTHING ID-related here is PLACEHOLDER until the item/pickup scripts are reverse-engineered.

ID plan (reserved block: BASE_ID .. BASE_ID + 999):
    +0   .. +99   boss / goal-adjacent locations  (boss kills)
    +100 .. +199  floor checks: id = +100 + (N-1) for Descent floor -N, N=1..100 (default on)
    +200 .. +299  (reserved: chests / shops / NPC quests, future)
    +500 .. +599  progression items (depth keys)
    +600 .. +699  useful items (reserved)
    +700 .. +799  filler items
    +800 .. +899  traps
"""

GAME_NAME = "Devil Spire"
BASE_ID = 7_470_000  # PLACEHOLDER - verify no clash with other worlds before any public release

LOCATION_OFFSET = 0
FLOOR_OFFSET = 100
ITEM_OFFSET = 500

NUM_FLOORS = 100  # Descent floors -1 .. -100 (-100 = Rhamdon / goal floor)
NUM_TIERS = 10  # floor tiers of 10 floors each: tier 0 = floors -1..-10, ... tier 9 = floors -91..-100
