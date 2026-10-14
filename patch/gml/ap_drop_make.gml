// ap_drop_make(key): create the item instance of a WEIGHTED received item for a ground pickup (ap_drop_spawn).
// key = received index * 10 + part (part = armor piece 0-3 of a Progressive Armor set). Progressive tier = copies received
// up to that index. Returns the instance, or -4 when the item is not a weighted item.
var idx = floor(argument0 / 10);
var part = argument0 mod 10;
var rel = global.ap_item_id[idx] - global.ap_base - 500;
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
else if (rel >= 160 && rel <= 163)
{
    var c = ap_copies(idx);
    if (rel == 160)
    {
        it = generate_weapon(floor(12.5 * min(c, 7)), (random(3) < 1) + (2 * irandom(11))); // same type roll as generate_equipment
    }
    else if (rel == 161)
    {
        it = generate_armor(floor(12.5 * min(c, 7)), min(part, 3)); // type 0-3: body, head, arms, legs
    }
    else if (rel == 162)
    {
        it = generate_shield(25 * min(c, 3));
    }
    else
    {
        it = generate_accessory(20 * min(c, 4), irandom(3));
    }
}
else if (rel == 151)
{
    it = generate_ring(irandom(35));
}
return it;
