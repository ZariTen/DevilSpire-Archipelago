// ap_chest_check(): called in the context of an obj_chest (interact) when the player opens it, or uses an already open
// one (pre-opened at floor generation). Counts each chest once; mimics (obj_skullcrab) and empty chests don't count.
// Sends the next unsent "Chest (Floors -a to -b) #k" of the floor's 10-floor band, up to chest_checks per band.
if (ap_counted || global.mode != 1 || global.level >= 0 || global.ap_stale || global.ap_chest_n <= 0)
{
    exit;
}
if (!instance_exists(item))
{
    exit;
}
if (item.object_index == obj_skullcrab)
{
    exit;
}
ap_counted = 1;
var n = -global.level;
var band = min(9, floor((n - 1) / 10));
if (global.ap_chest_cnt[band] < min(global.ap_chest_n, 5))
{
    ap_emit("L|" + string(floor(global.ap_base + 200 + (band * 5) + global.ap_chest_cnt[band])));
    global.ap_chest_cnt[band] += 1;
    ap_save_checks();
    with (instance_create(0, 0, obj_message))
    {
        text = "Archipelago: chest check " + string(global.ap_chest_cnt[band]) + "/" + string(min(global.ap_chest_n, 5)) + " (floors -" + string((band * 10) + 1) + " to -" + string((band * 10) + 10) + ")";
    }
}
