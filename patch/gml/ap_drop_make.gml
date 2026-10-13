// ap_drop_make(item_id): create the item instance of a WEIGHTED received item (potion packs, equipment, rings) for a
// ground pickup (ap_drop_spawn). Returns the instance, or -4 when the id is not a weighted item.
var rel = argument0 - global.ap_base - 500;
var it = -4;
if (rel == 120 || rel == 121 || rel == 122)
{
    if (rel == 120)
    {
        it = generate_potion(0); // Red Potion
    }
    else if (rel == 121)
    {
        it = generate_potion(25); // Blue Potion
    }
    else
    {
        it = generate_potion(99); // White Potion
    }
    if (rel != 122)
    {
        with (it)
        {
            count = 3;
            weight = 0.75;
        }
    }
}
else if (rel >= 140 && rel <= 148)
{
    var cat = floor((rel - 140) / 3); // 0 weapon, 1 armor, 2 accessory
    var lv = 25 * (((rel - 140) mod 3) + 1);
    if (cat == 0)
    {
        it = generate_weapon(lv, (random(3) < 1) + (2 * irandom(11))); // same type roll as generate_equipment
    }
    else if (cat == 1)
    {
        it = generate_armor(lv, irandom(3));
    }
    else
    {
        it = generate_accessory(lv, irandom(3));
    }
}
else if (rel == 149 || rel == 150)
{
    it = generate_shield(25 * (rel - 148));
}
else if (rel == 151)
{
    it = generate_ring(irandom(35));
}
return it;
