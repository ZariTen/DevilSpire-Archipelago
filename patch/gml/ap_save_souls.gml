// persist the highest received-item index whose Pouch of Souls was granted (line 1) and the slot id (line 2, may be empty)
var f = file_text_open_write("ap_souls_granted.txt");
if (f != -1)
{
    file_text_write_string(f, string(global.ap_souls_max));
    file_text_writeln(f);
    file_text_write_string(f, global.ap_slot_id);
    file_text_writeln(f);
    file_text_close(f);
}
