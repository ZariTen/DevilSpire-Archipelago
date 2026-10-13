// ap_save_granted(): COMMIT the run state, called together with the game's own save (next_floor, camp grant, new run)
// and on death / stale. Line 1 = items processed for the CURRENT run (-1 = no AP run active), line 2 = slot id,
// line 3 = indexes of weighted items still waiting on the ground ("," separated). Between saves this state lives only in
// memory, so quitting and choosing Continue rolls it back together with the character: nothing lost, nothing doubled.
var dl = "";
if (global.ap_granted >= 0)
{
    for (var i = 0; i < ds_list_size(global.ap_drops); i++)
    {
        if (i > 0)
        {
            dl += ",";
        }
        dl += string(ds_list_find_value(global.ap_drops, i));
    }
}
global.ap_commit_granted = global.ap_granted;
global.ap_commit_drops = dl;
ap_write_granted();
