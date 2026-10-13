// ap_grant_pending(): process every received-but-not-yet-processed item of the current run (index order): weightless items
// are applied directly, weighted ones are queued for the ground (ap_drop_spawn). Returns 1 when nothing is left pending, 0 when
// blocked by an ungrantable item (retried on the next poll; skipped after 5 failed attempts) or by the batch limit.
// Sets global.ap_cnt = items processed, global.ap_dcnt = how many of them went to the ground. Does NOT write
// ap_granted.txt: the caller commits (ap_save_granted) together with the character save.
global.ap_cnt = 0;
global.ap_dcnt = 0;
if (global.ap_granted < 0)
{
    return 0;
}
var ok = 1;
var budget = 100; // at most 100 items per call (no frame freeze / message flood with huge bursts)
while (global.ap_granted < global.ap_n && budget > 0)
{
    budget -= 1;
    global.ap_cur = global.ap_granted;
    var nd = ds_list_size(global.ap_drops);
    if (ap_grant_item(global.ap_item_id[global.ap_granted]))
    {
        global.ap_fail = 0;
        global.ap_granted += 1;
        global.ap_cnt += 1;
        if (ds_list_size(global.ap_drops) > nd)
        {
            global.ap_dcnt += 1;
        }
    }
    else
    {
        global.ap_fail += 1;
        ok = 0;
        if (global.ap_fail >= 5)
        {
            global.ap_fail = 0;
            global.ap_granted += 1; // give up on an ungrantable item (e.g. inventory full)
            ap_emit("E|skipped item idx " + string(global.ap_granted - 1));
        }
        break;
    }
}
return ok && global.ap_granted >= global.ap_n;
