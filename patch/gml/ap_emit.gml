// ap_emit(line): append one line to ap_out.txt (game -> client).
// Check/goal lines (L, G) are tagged with the slot id the game currently belongs to ("L|<id>|<slot_id>") so the
// client never sends checks of one multiworld to another. While stale (config switched to another multiworld
// during this session) L/G/D lines are suppressed.
var line = argument0;
var kind = string_char_at(line, 1);
if (variable_global_exists("ap_stale"))
{
    if (global.ap_stale && (kind == "L" || kind == "G" || kind == "D"))
    {
        exit;
    }
    if (kind == "L" || kind == "G")
    {
        line += "|" + global.ap_slot_id;
    }
}
var f = file_text_open_append("ap_out.txt");
if (f != -1)
{
    file_text_write_string(f, line);
    file_text_writeln(f);
    file_text_close(f);
}
