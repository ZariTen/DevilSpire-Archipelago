# Item catalog (Devil Spire AP) - grantable items, how they work, what we picked

Design (user decision): Slay-the-Spire style. **No gating**: all floors/bosses are reachable from the start, the multiworld is
always completable without outside items. Received items are power boosts that persist across deaths and are
**re-applied on every new run** (patch: `ap_granted` is reset by `ap_new_run`; consumables/gold/souls/equipment are
handed out again each run - accepted behaviour; stat boosts stack as the list is replayed onto a fresh character).
Item id = `base_id (7470000) + 500 + code`. Verified = read from the pristine code dump (CodeEntries); **no runtime test yet**.

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

## Candidate table
Recommendation: **Pool** = in the default pool, **Opt** = only as trap via option, **No** = skipped. "V" = verified from code, "G" = guess/untested behaviour.

| Item | Effect | How granted (patch) | Balance risk | Rec. | Basis |
|---|---|---|---|---|---|
| Orb of Strength/Intelligence/Vitality/Agility | +3 to that stat (+derived stats, same as boss red orb) | direct stat edit on obj_player (code copied from `interact`/obj_orb) | Strong (stacks per run; 18 orbs = +54 stats vs ~+30 from a full vanilla run's red orbs). Classified useful | Pool (4/4/6/4) | V code, G runtime |
| Stat Point | +1 unspent point to spend | `global.statpoints += 1` | Low | Pool (4) | V |
| Yellow Orb | 150-450 gold item | `generate_gold(irandom_range(150,450))` + `add_inventory` | Low (re-granted every run) | Pool (14) | V |
| Gold Hoard | 1000 gold | `generate_gold(1000)` | Low-med: shops/merchant scale | Pool (4) | V |
| Blue Orb | random stone (0-35) | `generate_stone(irandom(35))` | Low (player must apply to gear; may inventory-clutter) | Pool (10) | V |
| Pouch of Souls | +100 souls | `global.souls += 100; save_souls()` | Low; re-grant farms souls each run (meta currency for unlocks) | Pool (8) | V |
| Red Potion Pack | 3x full HP potion | `generate_potion(0)`, count 3, weight 0.75 | Low-med (stacks, 3 per item per run) | Pool (8) | V |
| Blue Potion Pack | 3x full MP | `generate_potion(25)`, count 3 | Low | Pool (4) | V |
| White Potion | full heal + cure | `generate_potion(99)` | Low | Pool (3) | V |
| Spell Page Basic/Advanced/Master | random spell of tier 0-11 / 12-23 / 24-47 | `generate_spell(irandom_range(..))` + `get_item` (grimoire) | Master spells (e.g. Abracadabra) strong; grimoire has 24 slots; full = item skipped | Pool (4/3/2); Master useful | V |
| Weapon Lv25/50/75 | random weapon (24 types, random roll) | `generate_weapon(L, type roll)` | L75 ~ atk 37 (x1.5 2h) = a floor ~70 drop; weight up to ~7-15 kg may overencumber a weak build | Pool (3/3/2) | V formulas, G balance |
| Armor Piece Lv25/50/75 | random slot (body/head/arms/legs) | `generate_armor(L, irandom(3))` | Weight (body L75 up to ~18 kg) | Pool (3/3/3) | V |
| Accessory Lv25/50/75 | charm, stats sum L/5 | `generate_accessory(L, irandom(3))` | Low | Pool (2/2/1) | V |
| Shield Lv25/50 | random shield/buckler/bulwark | `generate_shield(L)` | Low | Pool (1/2) | V |
| Mystic Ring | random ring (36 effects) | `generate_ring(irandom(35))` | Effect-dependent (some are situational) | Pool (3) | V |
| Ambush Trap | 3-5 enemies spawn next to player, alerted | `instance_create(.., obj_enemy)` | Can kill; live-only | Opt (trap) | V creation, G effect |
| Plague Trap | 1 random body + 1 random mind ailment | add to ailment timers | Mild | Opt (trap) | V |
| Pickpocket Trap | lose half the carried gold | halve `count` of gold stacks | Mild | Opt (trap) | V |
| Weaken trap (-stats) | lower a stat | would reuse artifact code (`global.str--`...) | Permanent for the run; unfair | No | V code exists, rejected |
| Artifacts | sacrifice X for Y | `generate_artifact` | Net-negative/complex | No | V |
| Oil, keys, lockpicks, skulls, trash | utility | `generate_*` | Low value | No | V |
| Depth keys | gating | - | removed by design decision | No | - |
| Level-up / XP | `global.xp`, `level_up()` | possible | Interacts with level scaling | No (Stat Point instead) | G |

## Final pool (default 110 = locations with floor checks "every floor")
Useful: Orb of Strength 4, Intelligence 4, Vitality 6, Agility 4, Stat Point 4, Spell Page (Master) 2, Weapon Lv50 3, Lv75 2, Armor Lv50 3, Lv75 3, Accessory Lv50 2, Lv75 1, Shield Lv50 2 (= 40).
Filler (70): Yellow Orb 14, Gold Hoard 4, Blue Orb 10, Pouch of Souls 8, Red Potion Pack 8, Blue Potion Pack 4, White Potion 3, Spell Page Basic 4 / Advanced 3, Weapon Lv25 3, Armor Lv25 3, Accessory Lv25 2, Shield Lv25 1, Mystic Ring 3.
Traps: none by default; `trap_percentage` converts that % of fillers into Ambush/Plague/Pickpocket.
No progression items. With fewer locations (floor checks every 5th/10th/off: 30/20/10) a random subset of the 110-item template is used.

## Open balance questions
- Whether re-granting equipment every run (about 28 pieces cluttering the 100-slot inventory) is wanted; maybe cap or merge.
- Tier levels (25/50/75) and orb counts are guesses; float-weight overencumbrance is not blocked (forced add) and slows the player.
- Traps fire only for items received live (`ap_live`), never replayed on a new run.
