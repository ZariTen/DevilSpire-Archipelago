// ap_shop_item(item): an "Archipelago Item" was bought or stolen (get_item). Sends "Shop Floor -N #k", marks it sent,
// destroys the item. Returns 1 (taken).
var s = argument0.ap_loc;
if (s >= 0 && s < 18 && !global.ap_stale)
{
    if (string_char_at(global.ap_shop_sent, s + 1) != "1")
    {
        ap_emit("L|" + string(floor(global.ap_base + 250 + s)));
        global.ap_shop_sent = string_copy(global.ap_shop_sent, 1, s) + "1" + string_delete(global.ap_shop_sent, 1, s + 1);
        ap_save_checks();
    }
}
with (argument0)
{
    instance_destroy();
}
with (instance_create(0, 0, obj_message))
{
    text = "Archipelago: shop check sent";
}
return 1;
