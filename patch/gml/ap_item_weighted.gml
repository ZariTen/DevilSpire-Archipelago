// ap_item_weighted(item_id): 1 for items that have weight in the game (potions 0.25 each, weapons/armor/accessories/shields
// by level, rings 0.1) -> ground pickups; 0 for weightless ones (stat orbs/points, gold, stones, souls, spellbook, traps) -> direct.
var rel = argument0 - global.ap_base - 500;
return ((rel >= 120 && rel <= 122) || rel == 151 || (rel >= 160 && rel <= 163));
