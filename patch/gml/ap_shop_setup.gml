// ap_shop_setup(): called by obj_dungeoncreator right after it created the 8 merchant stands (obj_shop). On the Descent
// shop floors -10..-90 (shoptime: |floor| mod 10 == 0, not a boss floor), up to 2 stands sell an "Archipelago Item"
// for 150 gold: one per still-unsent "Shop Floor -N #1/#2" check (ids fixed per floor and slot). Camp shop: never.
if (global.mode != 1 || global.ap_stale || global.level >= 0)
{
    exit;
}
var n = -global.level;
if (n < 10 || n > 90 || (n mod 10) != 0)
{
    exit;
}
var k = ((n / 10) - 1) * 2;
var slot = 0;
with (obj_shop)
{
    while (slot < 2 && string_char_at(global.ap_shop_sent, k + slot + 1) == "1")
    {
        slot += 1;
    }
    if (slot < 2 && ap_shop < 0 && dungeon != 0.5)
    {
        with (item)
        {
            instance_destroy();
        }
        item = ap_make_apitem(k + slot);
        ap_shop = k + slot;
        price = 150;
        texT = sprite_get_texture(spr_pricetags, (price / 50) - 1);
        slot += 1;
    }
}
