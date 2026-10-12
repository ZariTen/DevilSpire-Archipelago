# Devil Spire (fan-made Archipelago integration)

*Unofficial, fan-made, not affiliated with the game's developer. Everything marked PLACEHOLDER is provisional.*

## What does randomization do?
Only the **Descent** mode (100 floors) is involved. It is unlocked from the start by the patch.
Item pickups from other players are delivered as persistent unlocks/upgrades.

## Roguelike loop
Like Slay the Spire, a death ends the run: the Descent save is wiped. **All Archipelago items you have received are
re-granted on your new run**, and **boss checks you already made stay checked**. Progress in a multiworld is therefore
cumulative across runs.

## What is a location?
- **Floor checks** ("Reach Floor -N", on by default): every Descent floor -1 to -99, plus the final floor -100, is a
  check. The option **Floor Checks** sets the granularity: every floor (default, 100 checks), every 5th floor (20: -1, -6, -11, ...),
  every 10th floor (10: -1, -11, ...) or off. Floor N needs the depth keys of its 10-floor tier.
- **Boss checks** (always on, separate from floor checks): Slime (-9), Abomination (-19), Idol (-29),
  Golems (-39, the two Golems are ONE check), Dragon (-49), Snake (-59), Apparition (-69), Girl (-79),
  Robot (-89) and the floor -99 gauntlet (which also counts as the floor -99 check).

With default options there are 110 locations (10 boss + 100 floor), plus the Rhamdon victory event. The item pool
is 9 depth keys (fewer with starting depth) and the rest filler (or traps, per Trap Percentage).

## What is the goal?
Defeat **Rhamdon** on floor -100.

## What items can be received?
PLACEHOLDER: Depth Keys (progressive or individual) that unlock deeper 10-floor tiers; filler (souls pouch, orbs);
optional traps (weakness, monster swarm).

**Everything is re-granted every run.** Because of the reset loop, every received item, filler included
(Pouch of Souls, Red/Yellow/Blue Orb), is re-applied by the client/patch on each new Descent save - a pouch of
souls is not a one-time payout but a permanent head start each run. Traps are likewise re-applied each run.

## DeathLink
Optional. Dying sends a DeathLink; receiving one kills your character (new run, items re-granted).

## Item ID block
Base ID 7,470,000 (PLACEHOLDER); layout documented in `constants.py`.
