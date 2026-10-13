// ap_slot_check(cfgslot): compare the configured multiworld slot with the one this session belongs to.
// "" -> X: adopt X (game started before the client ever connected). X -> Y: stale until restart (no checks sent,
// no items read, run marked inactive so items are not granted from the wrong multiworld).
var cfgslot = argument0;
if (cfgslot == "" || cfgslot == global.ap_slot_id || global.ap_stale)
{
    exit;
}
if (global.ap_slot_id == "")
{
    global.ap_slot_id = cfgslot;
    ap_save_souls();
    ap_write_granted(); // committed state only (the live run may have unsaved progress)
    ap_emit("X|slot adopted");
    exit;
}
global.ap_stale = 1;
global.ap_granted = -1;
ds_list_clear(global.ap_drops);
ap_save_granted();
ap_emit("X|slot changed while running: restart the game");
with (instance_create(0, 0, obj_message))
{
    text = "Archipelago: different multiworld connected. Quit and restart the game.";
}
