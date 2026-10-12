// persist how many received items were already granted to the CURRENT run (-1 = no AP run active)
var f = file_text_open_write("ap_granted.txt");
if (f != -1)
{
    file_text_write_string(f, string(global.ap_granted));
    file_text_writeln(f);
    file_text_close(f);
}
