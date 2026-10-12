# Devil Spire (fan-made Archipelago integration)

*Unofficial, fan-made, not affiliated with the game's developer.*

## What does randomization do?
Only the **Descent** mode (100 floors) is involved. It is unlocked from the start by the patch.
Items from other players are delivered as persistent power boosts. **Nothing is gated**: every floor and boss is reachable from the start, and the multiworld is always completable without outside items (like Slay the Spire).

## Roguelike loop
Like Slay the Spire, a death ends the run: the Descent save is wiped. **All Archipelago items you have received are
re-granted on your new run**, and **boss checks you already made stay checked**. Progress in a multiworld is therefore
cumulative across runs.

## What is a location?
- **Floor checks** ("Reach Floor -N", on by default): every Descent floor -1 to -99, plus the final floor -100, is a
  check. The option **Floor Checks** sets the granularity: every floor (default, 100 checks), every 5th floor (20: -1, -6, -11, ...),
  every 10th floor (10: -1, -11, ...) or off.
- **Boss checks** (always on, separate from floor checks): Slime (-9), Abomination (-19), Idol (-29),
  Golems (-39, the two Golems are ONE check), Dragon (-49), Snake (-59), Apparition (-69), Girl (-79),
  Robot (-89) and the floor -99 gauntlet (which also counts as the floor -99 check).

With default options there are 110 locations (10 boss + 100 floor), plus the Rhamdon victory event. The item pool
is power boosts (see below); with fewer locations a random subset of the 110-item template is used. Traps replace filler per Trap Percentage.

## What is the goal?
Defeat **Rhamdon** on floor -100.

## What items can be received?
(Full details in the repo's `docs/item-catalog.md`; runtime effects are untested.)
- **Stat boosts (useful)**: Orb of Strength/Intelligence/Vitality/Agility (+3 to that stat), Stat Point (+1 unspent point).
- **Gold / stones / souls (filler)**: Yellow Orb (Gold) (150-450 gold), Gold Hoard (1000 gold), Blue Orb (Stone) (random Stone), Pouch of Souls (+100 souls).
- **Consumables (filler)**: Red Potion Pack (3 full-HP potions), Blue Potion Pack (3 full-MP), White Potion (full heal + cure).
- **Spell pages**: Basic / Advanced (filler), Master (useful): a random spell of that tier you do not know yet.
- **Equipment**: Weapon, Armor Piece, Accessory, Shield at level 25 (filler) / 50 / 75 (useful), and Mystic Rings (random ring).
- **Traps (optional, Trap Percentage)**: Ambush (enemies spawn), Plague (ailments), Pickpocket (lose half your gold).

**Everything except traps is re-granted every run.** Stat boosts stack and persist for the whole multiworld; consumables,
gold, souls and equipment are handed out again at the start of each new run (a permanent head start, not a one-time payout).
Traps fire once, when received while playing.

## DeathLink
Optional. Dying sends a DeathLink; receiving one kills your character (new run, items re-granted).

## Item ID block
Base ID 38,470,000; layout documented in `constants.py`.
