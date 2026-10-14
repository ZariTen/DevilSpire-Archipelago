// ap_slot_check(cfgslot): compare the configured multiworld slot with the one this session belongs to.
// "" -> X: adopt X (game started before the client ever connected).
// X -> Y outside the tower (title, menus, camp, dead): adopt Y live - per-slot state reset as for a fresh slot, any
// existing run of X is marked inactive (no items of Y go into it). A New Game then plays for Y without a restart.
// X -> Y while in the tower (a run of X): stale (no checks sent, no items read) until that run is left (death, quit,
// new game), then Y is adopted automatically.
var cfgslot = argument0;
if (cfgslot == "" || cfgslot == global.ap_slot_id)
{
    exit;
}
if (global.ap_slot_id == "")
{
    global.ap_slot_id = cfgslot;
    ap_save_souls();
    ap_save_checks();
    ap_write_granted(); // committed state only (the live run may have unsaved progress)
    ap_emit("X|slot adopted");
    exit;
}
var intower = (room == rom_dungeon && global.level < 0);
if (intower)
{
    if (!global.ap_stale)
    {
        global.ap_stale = 1;
        global.ap_granted = -1;
        ds_list_clear(global.ap_drops);
        ap_save_granted();
        ap_emit("X|slot changed during a run: stale until the run ends");
        with (instance_create(0, 0, obj_message))
        {
            text = "Archipelago: new seed connected - finish/quit this run to switch";
        }
    }
    exit;
}
// adopt the new slot live
global.ap_stale = 0;
global.ap_slot_id = cfgslot;
global.ap_granted = -1;
ds_list_clear(global.ap_drops);
global.ap_n = 0;
global.ap_loaded = 0;
global.ap_dl_init = 0;
global.ap_dl_pending = 0;
global.ap_fail = 0;
global.ap_souls_max = -1;
global.ap_msg_init = 0;
ap_save_souls();
ap_load_checks(cfgslot); // the client reset ap_checks.txt on the seed switch; another slot's file is not trusted
ap_save_checks();
ap_save_granted();
ap_emit("X|new slot adopted");
with (instance_create(0, 0, obj_message))
{
    text = "Archipelago: new seed connected";
}
