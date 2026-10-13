// called when the player's hp hits 0 (once per death)
if (global.mode != 1)
{
    exit;
}
global.ap_granted = -1;
ds_list_clear(global.ap_drops);
ap_save_granted();
if (global.ap_dl_recv)
{
    global.ap_dl_recv = 0;
    ap_emit("X|death caused by DeathLink");
}
else if (global.ap_deathlink)
{
    ap_emit("D|Died on floor " + string(global.level));
}
