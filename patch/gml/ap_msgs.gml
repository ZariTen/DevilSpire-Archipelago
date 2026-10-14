// ap_msgs(): "Sent <item> to <player>" popups. The client appends "idx|text" lines to ap_msgs.txt (idx increasing,
// last 20 kept). The first read only records the newest idx (no replay of old messages). Bulk sends are capped: at most
// 2 popups per poll plus "+N more".
if (!file_exists("ap_msgs.txt"))
{
    exit;
}
var f = file_text_open_read("ap_msgs.txt");
if (f == -1)
{
    exit;
}
var maxi = global.ap_msg_seq;
var shown = 0;
var more = 0;
while (!file_text_eof(f))
{
    var line = file_text_read_string(f);
    file_text_readln(f);
    var si = string_digits(ap_field(line, 0));
    if (string_length(si) > 0)
    {
        var i = real(si);
        if (i > global.ap_msg_seq)
        {
            if (global.ap_msg_init)
            {
                if (shown < 2)
                {
                    shown += 1;
                    var t = ap_field(line, 1);
                    with (instance_create(0, 0, obj_message))
                    {
                        text = "Archipelago: " + t;
                    }
                }
                else
                {
                    more += 1;
                }
            }
            maxi = max(maxi, i);
        }
    }
}
file_text_close(f);
global.ap_msg_seq = maxi;
global.ap_msg_init = 1;
if (more > 0)
{
    with (instance_create(0, 0, obj_message))
    {
        text = "Archipelago: +" + string(more) + " more sent";
    }
}
