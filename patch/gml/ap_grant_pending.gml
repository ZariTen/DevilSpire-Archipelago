// ap_grant_pending(): grant every received-but-not-yet-granted item of the current run (index order).
// Returns 1 when nothing is left pending, 0 when blocked by an ungrantable item (retried on the next chest open;
// skipped after 5 failed attempts). Sets global.ap_cnt = number of items granted by this call.
global.ap_cnt = 0;
if (global.ap_granted < 0)
{
    return 0;
}
var ok = 1;
var changed = 0;
var budget = 100; // at most 100 items per chest open (no frame freeze / message flood with huge bursts)
while (global.ap_granted < global.ap_n && budget > 0)
{
    budget -= 1;
    global.ap_cur = global.ap_granted;
    if (ap_grant_item(global.ap_item_id[global.ap_granted]))
    {
        global.ap_fail = 0;
        global.ap_granted += 1;
        global.ap_cnt += 1;
        changed = 1;
    }
    else
    {
        global.ap_fail += 1;
        ok = 0;
        if (global.ap_fail >= 5)
        {
            global.ap_fail = 0;
            global.ap_granted += 1; // give up on an ungrantable item (e.g. inventory full)
            changed = 1;
            ap_emit("E|skipped item idx " + string(global.ap_granted - 1));
        }
        break;
    }
}
if (changed)
{
    ap_save_granted();
}
return ok;
