// ap_emit(line): append one line to ap_out.txt (game -> client)
var f = file_text_open_append("ap_out.txt");
if (f != -1)
{
    file_text_write_string(f, argument0);
    file_text_writeln(f);
    file_text_close(f);
}
