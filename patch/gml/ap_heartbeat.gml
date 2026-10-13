// ap_heartbeat(): read ap_heartbeat.txt ("<counter>|<slot_id>|<slot name>", rewritten by the client every 3 s while it is
// connected and has the server's item list). Connected = the content changed within the last 10 s. The value present when
// the game starts only counts once it changes (a file left behind by a closed client is not "connected").
var line = "";
if (file_exists("ap_heartbeat.txt"))
{
    var f = file_text_open_read("ap_heartbeat.txt");
    if (f != -1)
    {
        line = file_text_read_string(f);
        file_text_close(f);
    }
}
if (!global.ap_hb_init)
{
    global.ap_hb_init = 1;
    global.ap_hb_val = line;
}
else if (line != global.ap_hb_val && line != "")
{
    global.ap_hb_val = line;
    global.ap_hb_time = current_time;
    global.ap_hb_name = ap_field(line, 2);
}
global.ap_connected = (global.ap_hb_time >= 0 && (current_time - global.ap_hb_time) < 10000);
if (global.ap_connected)
{
    global.ap_hb_seen = 1; // items are only handed out once the client was connected in this session
}
