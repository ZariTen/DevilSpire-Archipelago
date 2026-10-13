// ap_drop_taken(key): called from obj_droppeditem Destroy (= picked up; leaving the room does not fire Destroy) for one of our
// ground pickups. Removes the index from the pending ground list. Persisted with the character (ap_save_granted next to save_game).
var p = ds_list_find_index(global.ap_drops, argument0);
if (p >= 0)
{
    ds_list_delete(global.ap_drops, p);
}
ds_map_delete(global.ap_drop_inst, argument0);
