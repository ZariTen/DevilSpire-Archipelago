// ap_load_checks(cfgslot): read ap_checks.txt (see ap_save_checks); ignored if it belongs to another slot. An older
// line 1 (chest counts per band) is not 99 flags and is simply reset.
global.ap_lock_sent = string_repeat("0", 99);
global.ap_shop_sent = string_repeat("0", 18);
if (file_exists("ap_checks.txt"))
{
    var f = file_text_open_read("ap_checks.txt");
    if (f != -1)
    {
        var l1 = file_text_read_string(f);
        file_text_readln(f);
        var l2 = file_text_read_string(f);
        file_text_readln(f);
        var l3 = file_text_read_string(f);
        file_text_close(f);
        if (argument0 == "" || l3 == "" || l3 == argument0)
        {
            if (string_length(l1) == 99 && string_count("0", l1) + string_count("1", l1) == 99)
            {
                global.ap_lock_sent = l1;
            }
            if (string_length(l2) == 18 && string_count("0", l2) + string_count("1", l2) == 18)
            {
                global.ap_shop_sent = l2;
            }
        }
        else
        {
            ap_emit("X|slot changed, locked chest/shop check state reset");
        }
    }
}
