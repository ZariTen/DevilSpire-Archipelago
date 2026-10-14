// Archipelago patch: read ap_config.ini and set up state. Called once from obj_setup Alarm 0.
global.ap_ready = 1;
global.ap_stale = 0;
global.ap_slot_id = "";
global.ap_deathlink = 0;
global.ap_floor_step = 2;
global.ap_base = 38470000;
global.ap_poll_frames = 30;
global.ap_difficulty = 3; // Extreme until the client wrote ap_config.ini
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
global.ap_dcnt = 0;
global.ap_hb_init = 0;
global.ap_hb_val = "";
global.ap_hb_time = -1;
global.ap_hb_name = "";
global.ap_hb_seen = 0;
global.ap_hb_warned = 0;
global.ap_connected = 0;
global.ap_msg_init = 0;
global.ap_msg_seq = 0;
// weighted items of the current run still waiting on the ground (received-item indexes) and their live obj_droppeditem
global.ap_drops = ds_list_create();
global.ap_drop_inst = ds_map_create();
global.ap_commit_granted = -1;
global.ap_commit_drops = "";
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
        var dl = "";
        if (!file_text_eof(f))
        {
            gslot = file_text_read_string(f);
            file_text_readln(f);
            if (!file_text_eof(f))
            {
                dl = file_text_read_string(f); // line 3: pending ground items "i,j,k" (missing in older builds)
            }
        }
        file_text_close(f);
        while (string_length(dl) > 0)
        {
            var cp = string_pos(",", dl);
            var tok = dl;
            if (cp > 0)
            {
                tok = string_copy(dl, 1, cp - 1);
                dl = string_delete(dl, 1, cp);
            }
            else
            {
                dl = "";
            }
            tok = string_digits(tok);
            if (string_length(tok) > 0)
            {
                if (ds_list_find_index(global.ap_drops, real(tok)) < 0)
                {
                    ds_list_add(global.ap_drops, real(tok));
                }
            }
        }
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
    ds_list_clear(global.ap_drops);
    ap_emit("X|slot changed, run inactive");
}
if (global.ap_granted < 0)
{
    ds_list_clear(global.ap_drops);
}
ap_load_checks(cfgslot);
ap_save_checks();
ap_save_granted();
ap_emit("S|9|@AP_MOD_LABEL@"); // S|<patch protocol version>|<mod label>: the client warns when either does not match
