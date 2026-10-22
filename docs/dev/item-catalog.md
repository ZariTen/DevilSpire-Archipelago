# Item catalog

Design: Slay-the-Spire style. **No gating**: all floors/bosses are reachable from the start, the multiworld is
always completable without outside items. Received items are power boosts that persist across deaths and are
**re-applied on every new run** (`ap_granted` is reset by `ap_new_run`; consumables, gold and equipment come again each
run; souls only once per slot; gear only the best tier).
Item id = `base_id (38470000) + 500 + code`. "Verified" = read from the decompiled code (local, git-ignored).

## How the game creates/gives items (VERIFIED from code)
- `generate_*` scripts create an item *instance* at (0,0) and return it; `get_item(inst)` (run as obj_player) adds it:
  `add_inventory(inst, -4, 1)` (slot -4 = first free of 100 slots; 3rd arg 1 = refuse when `carrying >= maxcarry` unless weight 0),
  fires achievements, auto-assigns shortcut slots (weapons/shields/potions). `obj_spell` goes to `add_grimoire` (24 slots;
  returns 0 when full). If adding fails the caller must `instance_destroy` the instance. Quirk: `add_inventory` returns `-4` (truthy!)
  when the 100 slots are full, so the patch checks `== 1`.
- Potions, `obj_misc` (except moneybag type 1 and stones type 16) stack: `count`/`weight` are summed into an existing stack.
- "Level" argument `L` of the generators: dungeon drops use `abs(global.level) + random(5..20)` (floor depth + noise); sprite tier = `min(floor(L/10), n-1)` (10 tiers: Rusty..Legendary), stats scale ~linearly with L (no cap):
  - weapon: `atk = L/2` (x1.5 two-handed) x rng(0.75-1.25), weight `L*0.1` (x2 two-handed), durability `L*250`; 24 types (0 Knives,1 Bow,2 Hatchets,3 Crossbow,4 Javelins,5 Musket,6 Flintlock,7 Glaives, 8 Shortsword ... 23 Chain; even/odd = 1h/2h variants). Drop roll: `(random(3)<1) + 2*irandom(11)`. 10% chance of an enchantment. `atk >= 100` = achievement "Legendary Sword".
  - armor (type 0 body,1 head,2 arms,3 legs; random 3 variants): body `def = 0.4*L (x2 for the second variant)`, head 0.15, arms 0.25, legs 0.2, weight `0.08*L` (x3 variant) etc.
  - accessory (charm, 3 stats summing to `round(L/5)`), shield (`stagger = 3 + 0.05*L`, 3 kinds), ring (type 0-35 = same 36 effects as stones; has an effect only, no L).
  - potions by roll r: <20 Red(type1: full HP), <40 Blue(2: full MP), <55 Orange(5: cure body), <70 Green(6: cure mind), <80 Purple(3: random ailment), <90 Yellow(4: cure all), <95 Black(0: random HP), else White(7: full heal+cure). `obj_potion`: count 1, weight 0.25.
  - spells: 48 types (0-47). Treasure tiers: 0-11 basic (Fireball..Symbol of Pain), 12-23 (Telekinesis..Drain), 24-28, 29-47 (Mend Wounds..Abracadabra). `generate_spell` skips types you already know (`spell_exists`).
  - stones: `generate_stone(0..35)` (boss blue orb: `irandom(35)`, re-rolled if the enchant is already owned); stones are applied to equipment manually. *Correction vs the earlier patch (which used 0-23): the game uses 0-35.*
  - gold: `generate_gold(n)` = obj_misc type 15 (weight 0); moneybag = type 1 (weight `n*0.01`). Boss yellow orb gives `irandom_range(150,450)` gold; dungeon moneybags 2-98.
  - orbs: `obj_orb` iam 0 red (+3 to STR/INT/VIT/AGI, `igive`=0..3, same code as the patch), 1 yellow (gold), 2 blue (stone). Each boss floor drops one of each (+ dark rooms).
  - souls: `global.souls` = persistent meta currency (+ drops from enemies at death); spent on unlocks (1000-9999) and the 250-soul crystal in a run; `save_souls()` persists.
  - `global.statpoints` is incremented by every level-up (`level_up`) and spent in the character sheet.
  - artifacts (`generate_artifact`): sacrifice-for-benefit pairs (e.g. lose STR for something) - NOT suitable as a free boost. Skipped.
  - oil (lantern fuel `obj_oil`), keys (`generate_key`, type 99), lockpicks (type 2), skulls (arena/village currency), trash: possible but low value; skipped.
- Enemy spawn: `instance_create(x, y, obj_enemy)` runs `obj_enemy Create`, which picks `character_sheet(1 + 3*dungeon + irandom(2))` (floor-appropriate). Status ailments are plain player vars (`poison`, `cramp`, `root`, `paralysis`, `headache`, `mute`, `blind`, `confusion`, duration `600/bodyres|mindres` like a purple potion).

## Items
"Pool (n)" = count in the default pool, "Opt" = trap via option. "V" = verified from code, "G" = guess.

| Item | Effect | How granted (patch) | Balance risk | Rec. | Basis |
|---|---|---|---|---|---|
| Orb of Strength/Intelligence/Vitality/Agility | +3 to that stat (+derived stats, same as boss red orb) | direct stat edit on obj_player (code copied from `interact`/obj_orb) | Strong (stacks per run; 18 orbs = +54 stats vs ~+30 from a full vanilla run's red orbs). Classified useful | Pool (5/5/7/5) | V code, G runtime |
| Stat Point | +1 unspent point to spend | `global.statpoints += 1` | Low | Pool (5) | V |
| Yellow Orb (Gold) | 150-450 gold item | `generate_gold(irandom_range(150,450))` + `add_inventory` | Low (re-granted every run) | Pool (16) | V |
| Gold Hoard | 1000 gold | `generate_gold(1000)` | Low-med: shops/merchant scale | Pool (4) | V |
| Blue Orb (Stone) | random stone (0-35) | `generate_stone(irandom(35))` | Low (player must apply to gear; may inventory-clutter) | Pool (10) | V |
| Pouch of Souls | +100 souls | `global.souls += 100; save_souls()` | Low; re-grant farms souls each run (meta currency for unlocks) | Pool (8) | V |
| Red Potion Pack | 3x full HP potion | `generate_potion(0)`, count 3, weight 0.75 | Low-med (stacks, 3 per item per run) | Pool (8) | V |
| Blue Potion Pack | 3x full MP | `generate_potion(25)`, count 3 | Low | Pool (4) | V |
| White Potion | full heal + cure | `generate_potion(99)` | Low | Pool (3) | V |
| Progressive Spellbook | copy 1-2: Basic spell (0-11), 3-4: Advanced (12-23), 5-6: Master (24-47) | `generate_spell` + `get_item` (grimoire); every copy re-granted each run | Master spells strong | Pool (6), progression | V |
| Progressive Weapon | copy N: random weapon at L = floor(12.5N) (12..87) | `generate_weapon(L, type roll)`, ground pickup | see tiers below | Pool (7), progression | V formulas, G balance |
| Progressive Armor | copy N: full set (body, head, arms, legs) at L = floor(12.5N) | `generate_armor(L, 0..3)`, 4 ground pickups | Weight of a full set | Pool (7), progression | V |
| Progressive Shield | copy N: shield at L = 25N (25/50/75) | `generate_shield(25N)` | Low | Pool (3), progression | V |
| Progressive Accessory | copy N: charm at L = 20N (20/40/60/80) | `generate_accessory(20N, irandom(3))` | Low | Pool (4), progression | V |
| Mystic Ring | random ring (36 effects) | `generate_ring(irandom(35))` | Effect-dependent (some are situational) | Pool (3) | V |
| Ambush Trap | 3-5 enemies spawn next to player, alerted | `instance_create(.., obj_enemy)` | Can kill; live-only | Opt (trap) | V creation, G effect |
| Plague Trap | 1 random body + 1 random mind ailment | add to ailment timers | Mild | Opt (trap) | V |
| Pickpocket Trap | lose half the carried gold | halve `count` of gold stacks | Mild | Opt (trap) | V |

### Tier levels
Normal drops on floor -N are level N + 0..10 (chests, enemies), N + 10..20 (locked chests), N + 0..20 (shops); start gear
is 6-14. Copy k of c arrives around floor 100k/(c+1), so the tiers sit a little (~5-10 levels) behind normal drops there:

| Item | Levels |
|---|---|
| Progressive Weapon / Armor | 12, 25, 37, 50, 62, 75, 87 (floor of 12.5k) |
| Progressive Shield | 25, 50, 75 |
| Progressive Accessory | 20, 40, 60, 80 |

## Pool
A 110-item template. More locations: the extra slots get the template's useful + filler mix scaled up (largest
remainder; never more progressive copies). Fewer: filler is trimmed first, then useful, then progressive copies (safe,
nothing gates). Default (158 locations):

| Item | template | extra | total |
|---|---|---|---|
| Progressive Weapon / Armor / Shield / Accessory / Spellbook | 7 / 7 / 3 / 4 / 6 | 0 | 27 |
| Orb of Strength / Intelligence / Agility | 5 each | 3 each | 8 each |
| Orb of Vitality | 7 | 4 | 11 |
| Stat Point | 5 | 3 | 8 |
| Yellow Orb (Gold) | 16 | 9 | 25 |
| Gold Hoard | 4 | 2 | 6 |
| Blue Orb (Stone) | 10 | 6 | 16 |
| Pouch of Souls | 8 | 5 | 13 |
| Red Potion Pack | 8 | 4 | 12 |
| Blue Potion Pack | 4 | 2 | 6 |
| White Potion | 3 | 2 | 5 |
| Mystic Ring | 3 | 2 | 5 |
| **Total** | 110 | 48 | 158 (27 progression, 43 useful, 88 filler) |

- Progressive copy N = the Nth copy in received order (counted in `ap_in.txt`). Per run only the best gear tier is given;
  the spellbook gives every copy.
- Traps: none by default; `trap_percentage` turns that % of filler into Ambush/Plague/Pickpocket. Traps fire only for
  items received live, never on a new run.
- Retired item codes 130-132 and 140-150 are not reused.

## Open balance questions
- Re-granting equipment every run clutters the 100-slot inventory; maybe cap or merge.
- Orb counts are guesses. Over-encumbrance is not blocked (forced add) and slows the player.
