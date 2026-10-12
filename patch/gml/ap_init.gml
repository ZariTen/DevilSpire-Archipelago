// Archipelago patch: read ap_config.ini and set up state. Called once from obj_setup Alarm 0.
global.ap_ready = 1;
ini_open("ap_config.ini");
global.ap_deathlink = ini_read_real("ap", "death_link", 0);
global.ap_floor_step = ini_read_real("ap", "floor_check_step", 1);
global.ap_base = ini_read_real("ap", "base_id", 7470000);
global.ap_poll_frames = ini_read_real("ap", "poll_frames", 30);
ini_close();
global.ap_tick = 0;
global.ap_n = 0;
global.ap_loaded = 0;
global.ap_dl_init = 0;
global.ap_dl_seq = 0;
global.ap_dl_pending = 0;
global.ap_dl_text = "";
global.ap_dl_recv = 0;
global.ap_fail = 0;
global.ap_granted = -1;
global.ap_keys = 0;
if (file_exists("ap_granted.txt"))
{
    var f = file_text_open_read("ap_granted.txt");
    if (f != -1)
    {
        var s = string_digits(file_text_read_string(f));
        file_text_close(f);
        if (string_length(s) > 0)
        {
            global.ap_granted = real(s);
        }
    }
}
ap_emit("S|1|patch started");
