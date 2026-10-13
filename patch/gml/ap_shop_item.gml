// ap_shop_item(item): an "Archipelago Item" was taken (get_item): bought/stolen in a shop (ap_loc 0..17 = "Shop Floor
// -N #k") or taken from a locked chest (ap_loc 1000 + N = "Locked Chest Floor -N"). Sends the check once, marks it
// sent, destroys the item. Returns 1 (taken).
var s = argument0.ap_loc;
if (!global.ap_stale)
{
    if (s >= 0 && s < 18)
    {
        if (string_char_at(global.ap_shop_sent, s + 1) != "1")
        {
            ap_emit("L|" + string(floor(global.ap_base + 250 + s)));
            global.ap_shop_sent = string_copy(global.ap_shop_sent, 1, s) + "1" + string_delete(global.ap_shop_sent, 1, s + 1);
            ap_save_checks();
        }
    }
    else if (s >= 1001 && s <= 1099)
    {
        var n = s - 1000;
        if (string_char_at(global.ap_lock_sent, n) != "1")
        {
            ap_emit("L|" + string(floor(global.ap_base + 300 + n)));
            global.ap_lock_sent = string_copy(global.ap_lock_sent, 1, n - 1) + "1" + string_delete(global.ap_lock_sent, 1, n);
            ap_save_checks();
        }
    }
}
with (argument0)
{
    instance_destroy();
}
with (instance_create(0, 0, obj_message))
{
    text = "Archipelago: check sent";
}
return 1;
