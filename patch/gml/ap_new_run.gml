// ap_new_run(mode): called when a new character is created. A new Descent run re-applies ALL received items.
if (argument0 == 1)
{
    global.ap_granted = 0;
    global.ap_fail = 0;
    ds_list_clear(global.ap_drops);
    ds_map_clear(global.ap_drop_inst);
    ap_save_granted();
    ap_emit("N|1|new descent run");
}
