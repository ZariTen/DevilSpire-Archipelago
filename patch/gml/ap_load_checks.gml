// ap_load_checks(cfgslot): read ap_checks.txt (see ap_save_checks); ignored if it belongs to another slot.
for (var b = 0; b < 10; b++)
{
    global.ap_chest_cnt[b] = 0;
}
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
            var b = 0;
            while (string_length(l1) > 0 && b < 10)
            {
                var cp = string_pos(",", l1);
                var tok = l1;
                if (cp > 0)
                {
                    tok = string_copy(l1, 1, cp - 1);
                    l1 = string_delete(l1, 1, cp);
                }
                else
                {
                    l1 = "";
                }
                tok = string_digits(tok);
                if (string_length(tok) > 0)
                {
                    global.ap_chest_cnt[b] = real(tok);
                }
                b += 1;
            }
            if (string_length(l2) == 18 && string_count("0", l2) + string_count("1", l2) == 18)
            {
                global.ap_shop_sent = l2;
            }
        }
        else
        {
            ap_emit("X|slot changed, chest/shop check state reset");
        }
    }
}
