"""Shared constants. BASE_ID = 38_470_000 (fixed; changing it breaks all existing yamls/seeds).

ID plan (reserved block: BASE_ID .. BASE_ID + 999):
    +0   .. +99   boss / goal-adjacent locations  (boss kills)
    +100 .. +199  floor checks: id = +100 + (N-1) for Descent floor -N, N=1..100 (default on)
    +200 .. +249  chest checks: +200 + band*5 + k (band 0..9 = floors -1..-10, ...; k = 0..4)
    +250 .. +267  shop checks: +250 + (N/10 - 1)*2 + s for shop floor -N (N = 10..90), stand s = 0..1
    ITEM ids = BASE_ID + ITEM_OFFSET(500) + code, codes documented in items.py / docs/dev/item-catalog.md:
    +100..+104 stat boosts, +110..+113 gold/stone/souls, +120..+122 potions, +130..+132 spell pages,
    +140..+151 equipment, +200..+202 traps. (No keys / progression items: nothing gates anything.)
"""

GAME_NAME = "Devil Spire"
BASE_ID = 38_470_000  # fixed final base ID (distinctive range, 38,470,000..38,470,999); do not change

LOCATION_OFFSET = 0
FLOOR_OFFSET = 100
CHEST_OFFSET = 200
SHOP_OFFSET = 250
ITEM_OFFSET = 500

NUM_FLOORS = 100  # Descent floors -1 .. -100 (-100 = Rhamdon / goal floor)
NUM_TIERS = 10  # floor tiers of 10 floors each (regions for readability only; NO gating): tier 0 = floors -1..-10, ... tier 9 = floors -91..-100

PATCH_PROTOCOL = 7  # must match ap_init.gml "S|<n>|patch started"; bump together with GML changes
