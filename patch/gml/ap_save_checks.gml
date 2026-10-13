// ap_save_checks(): persist chest/shop check progress (ap_checks.txt). Line 1 = chest checks sent per 10-floor band
// ("c0,...,c9"), line 2 = shop checks sent (18 flags "0"/"1": floor -10 #1, #2, -20 #1, ...), line 3 = slot id.
// Cumulative over runs for the slot (checks are permanent); the client backs it up and resets it on a multiworld switch.
var s = "";
for (var b = 0; b < 10; b++)
{
    if (b > 0)
    {
        s += ",";
    }
    s += string(global.ap_chest_cnt[b]);
}
var f = file_text_open_write("ap_checks.txt");
if (f != -1)
{
    file_text_write_string(f, s);
    file_text_writeln(f);
    file_text_write_string(f, global.ap_shop_sent);
    file_text_writeln(f);
    file_text_write_string(f, global.ap_slot_id);
    file_text_writeln(f);
    file_text_close(f);
}
