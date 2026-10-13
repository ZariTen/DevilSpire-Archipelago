// ap_drop_spawn(): make sure every pending weighted item (global.ap_drops) lies on the ground of the current room as a native
// obj_droppeditem (picked up with the game's own interact/get_item, encumbrance included). Called from ap_poll while the player
// is alive in rom_dungeon. Room changes / restarts remove the instances without Destroy, so untaken items are simply spawned again.
// Camp (level 0.5): tidy grid around the player's arrival point (0,212). Tower: small grid around the player.
// At most 60 on the ground at once; the rest follow as items are picked up.
var n = ds_list_size(global.ap_drops);
if (n == 0)
{
    exit;
}
var present = 0;
for (var i = 0; i < n; i++)
{
    var idx = ds_list_find_value(global.ap_drops, i);
    if (ds_map_exists(global.ap_drop_inst, idx))
    {
        if (instance_exists(ds_map_find_value(global.ap_drop_inst, idx)))
        {
            present += 1;
        }
    }
}
var ax = obj_player.x;
var ay = obj_player.y;
var sp = 16;
var rmax = 3;
if (global.level == 0.5)
{
    ax = 0;
    ay = 212;
    sp = 20;
    rmax = 6;
}
var spawned = 0;
for (var i = 0; i < n && present < 60; i++)
{
    var idx = ds_list_find_value(global.ap_drops, i);
    var have = 0;
    if (ds_map_exists(global.ap_drop_inst, idx))
    {
        have = instance_exists(ds_map_find_value(global.ap_drop_inst, idx));
    }
    if (have || idx >= global.ap_n)
    {
        continue;
    }
    var it = ap_drop_make(global.ap_item_id[idx]);
    if (!instance_exists(it))
    {
        // not a weighted item (should not happen): drop it from the list
        ds_list_delete(global.ap_drops, i);
        i -= 1;
        n -= 1;
        ap_emit("E|bad ground item idx " + string(idx));
        continue;
    }
    var d = instance_create(ax, ay, obj_droppeditem);
    var found = 0;
    with (d)
    {
        mask_index = spr_player; // test with the player's footprint: the spot must be walkable
        for (var r = 1; r <= rmax && !found; r++)
        {
            for (var gy = -r; gy <= r && !found; gy++)
            {
                for (var gx = -r; gx <= r && !found; gx++)
                {
                    if (max(abs(gx), abs(gy)) == r)
                    {
                        x = ax + (gx * sp);
                        y = ay + (gy * sp);
                        if (place_free(x, y) && !place_meeting(x, y, obj_droppeditem) && !place_meeting(x, y, obj_decor) && !place_meeting(x, y, obj_shade) && !place_meeting(x, y, obj_bonfire) && !place_meeting(x, y, obj_entrance) && !place_meeting(x, y, obj_tombstone))
                        {
                            found = 1;
                        }
                    }
                }
            }
        }
        if (!found)
        {
            x = ax; // no free grid spot: put it where the player stands / arrives (always reachable)
            y = ay;
        }
        mask_index = -1;
        item = it;
        ap_idx = idx;
    }
    ds_map_delete(global.ap_drop_inst, idx);
    ds_map_add(global.ap_drop_inst, idx, d);
    present += 1;
    spawned += 1;
}
if (spawned > 0 && global.level != 0.5)
{
    audio_play_sound(snd_treasure, 1, false);
}
return spawned;
