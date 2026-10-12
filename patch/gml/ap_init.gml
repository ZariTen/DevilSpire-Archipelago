// Archipelago patch: read ap_config.ini and set up state. Called once from obj_setup Alarm 0.
global.ap_ready = 1;
global.ap_stale = 0;
global.ap_slot_id = "";
global.ap_deathlink = 0;
global.ap_floor_step = 1;
global.ap_base = 38470000;
global.ap_poll_frames = 30;
var cfgslot = ap_read_config();
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
global.ap_cur = 0;
global.ap_tmp = 0;
global.ap_cnt = 0;
global.ap_chest_spawn = 0;
// souls are granted only ONCE per slot: highest received-item index whose Pouch of Souls was already granted (-1 = none)
global.ap_souls_max = -1;
global.ap_slot_id = cfgslot;
var stored = "";
var gslot = "";
if (file_exists("ap_souls_granted.txt"))
{
    var sf = file_text_open_read("ap_souls_granted.txt");
    if (sf != -1)
    {
        var sml = file_text_read_string(sf);
        var sm = string_digits(sml);
        if (string_char_at(sml, 1) == "-")
        {
            sm = ""; // "-1" = none granted (string_digits would turn it into 1)
        }
        file_text_readln(sf);
        if (!file_text_eof(sf))
        {
            stored = file_text_read_string(sf);
        }
        file_text_close(sf);
        if (string_length(sm) > 0)
        {
            global.ap_souls_max = real(sm);
        }
    }
}
if (cfgslot != "" && stored != "" && stored != cfgslot)
{
    global.ap_souls_max = -1; // different multiworld seed / slot: souls may be granted again
    ap_emit("X|slot changed, souls grant state reset");
}
ap_save_souls();
if (file_exists("ap_granted.txt"))
{
    var f = file_text_open_read("ap_granted.txt");
    if (f != -1)
    {
        var gl = file_text_read_string(f);
        file_text_readln(f);
        if (!file_text_eof(f))
        {
            gslot = file_text_read_string(f);
        }
        file_text_close(f);
        var s = string_digits(gl);
        if (string_length(s) > 0)
        {
            global.ap_granted = real(s);
            if (string_char_at(gl, 1) == "-")
            {
                global.ap_granted = -1;
            }
        }
    }
}
if (cfgslot != "" && gslot != "" && gslot != cfgslot)
{
    global.ap_granted = -1; // run belongs to another multiworld: no items until a new character is created
    ap_emit("X|slot changed, run inactive");
}
ap_save_granted();
ap_emit("S|3|patch started"); // S|<patch protocol version>: the client warns when it does not match
