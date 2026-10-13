// ap_leave_room(): prepended to next_floor (global.level is still the floor being LEFT). Leaving the camp (level 0.5):
// weighted items left on the camp ground are forfeited for this run (they come back next run with the normal re-grant).
// The list is only written by the save that follows in next_floor, so Continue in the camp still restores them.
// Mid-run drops (tower floors) keep following the player until picked up.
if (global.level == 0.5 && global.ap_granted >= 0)
{
    if (ds_list_size(global.ap_drops) > 0)
    {
        ap_emit("X|" + string(ds_list_size(global.ap_drops)) + " camp ground items left behind");
    }
    ds_list_clear(global.ap_drops);
    ds_map_clear(global.ap_drop_inst);
}
