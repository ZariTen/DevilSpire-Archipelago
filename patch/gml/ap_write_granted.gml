// ap_write_granted(): write the last committed run state (see ap_save_granted) to ap_granted.txt
var f = file_text_open_write("ap_granted.txt");
if (f != -1)
{
    file_text_write_string(f, string(global.ap_commit_granted));
    file_text_writeln(f);
    file_text_write_string(f, global.ap_slot_id);
    file_text_writeln(f);
    file_text_write_string(f, global.ap_commit_drops);
    file_text_writeln(f);
    file_text_close(f);
}
