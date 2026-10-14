// ap_read_config(): (re)read ap_config.ini. Called at start (ap_init) and on every poll, so the client may be
// started before or after the game. Returns the slot_id in the file ("" if none / no file).
var slot = "";
if (file_exists("ap_config.ini"))
{
    ini_open("ap_config.ini");
    global.ap_deathlink = ini_read_real("ap", "death_link", global.ap_deathlink);
    global.ap_floor_step = ini_read_real("ap", "floor_check_step", global.ap_floor_step);
    global.ap_base = ini_read_real("ap", "base_id", global.ap_base);
    global.ap_difficulty = ini_read_real("ap", "difficulty", global.ap_difficulty);
    global.ap_poll_frames = max(1, ini_read_real("ap", "poll_frames", global.ap_poll_frames));
    slot = ini_read_string("ap", "slot_id", "");
    ini_close();
}
return slot;
