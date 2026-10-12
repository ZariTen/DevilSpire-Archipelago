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
Boss kills: Slime (-9), Abomination (-19), Idol (-29), Golems (-39), Dragon (-49), Snake (-59), Apparition (-69),
Girl (-79), Robot (-89) and the floor -99 gauntlet. *(Optional, disabled stub: "Reach Floor -N" milestones.)*

## What is the goal?
Defeat **Rhamdon** on floor -100.

## What items can be received?
PLACEHOLDER: Depth Keys (progressive or individual) that unlock deeper 10-floor tiers; filler (souls pouch, orbs);
optional traps (weakness, monster swarm).

## DeathLink
Optional. Dying sends a DeathLink; receiving one kills your character (new run, items re-granted).

## Item ID block
Base ID 7,470,000 (PLACEHOLDER); layout documented in `constants.py`.
