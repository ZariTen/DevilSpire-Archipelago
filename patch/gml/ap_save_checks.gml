// ap_save_checks(): persist locked-chest/shop check progress (ap_checks.txt). Line 1 = locked chest checks sent
// (99 flags "0"/"1", floor -1 .. -99), line 2 = shop checks sent (18 flags: floor -10 #1, #2, -20 #1, ...), line 3 = slot.
// Cumulative over runs for the slot (checks are permanent); the client backs it up and resets it on a multiworld switch.
var f = file_text_open_write("ap_checks.txt");
if (f != -1)
{
    file_text_write_string(f, global.ap_lock_sent);
    file_text_writeln(f);
    file_text_write_string(f, global.ap_shop_sent);
    file_text_writeln(f);
    file_text_write_string(f, global.ap_slot_id);
    file_text_writeln(f);
    file_text_close(f);
}
