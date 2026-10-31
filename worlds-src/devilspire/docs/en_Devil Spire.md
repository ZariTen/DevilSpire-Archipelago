# Devil Spire

Unofficial fan project. You need your own Steam copy of the game.

## What changes?
One mode, **Archipelago**: 100 floors down the tower. The game locks no floor, but the logic only expects floors -1 to -20
at the start. Deeper floors expect Progressive Weapon and Armor: 1 of each for -21, up to 6 of each for -91 to -100.
The difficulty is set by the yaml (default Extreme) and locked in game.

## What is the goal?
Beat Rhamdon on floor -100.

## What are the checks?
- **Bosses:** floors -9, -19, ... -99 (10).
- **Floors:** every 2nd floor by default (option `floor_checks`).
- **Locked chests:** one per floor, with its key on the floor (not on boss or shop floors; 80).
- **Shops:** on floors -10 to -90, 2 stands sell an Archipelago Item for 150 gold (18).

An Archipelago Item shows what it holds and for whom.

## What items can I get?
- Stat orbs and stat points.
- Gold, stones, souls, potion packs, Mystic Rings.
- Progressive Weapon, Armor (full set), Shield and Accessory: each copy is a better tier.
- Progressive Spellbook: a new spell per copy (Basic, Advanced, Master).
- Traps, if the host turns them on.

## How do I get them?
At the camp: stat boosts, gold, stones and spells go straight to you; equipment, rings and potions lie on the ground.
When you die, the next run gives you all your items again (gear: your best tier). Souls are given once.

## DeathLink
Optional. Deaths are shared, but only while you are inside the tower.
