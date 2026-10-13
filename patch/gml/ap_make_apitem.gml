// ap_make_apitem(shop_slot): the "Archipelago Item" sold in tower shops (obj_misc type 77; buying/stealing it goes
// through get_item -> ap_shop_item, which sends the check instead of adding it to the inventory).
var it = instance_create(0, 0, obj_misc);
with (it)
{
    name = "Archipelago Item";
    type = 77;
    count = 1;
    weight = 0;
    sprite_index = spr_apicon;
    image_index = 0;
    dropped = spr_Dapicon;
    ap_loc = argument0;
}
return it;
