// ap_make_apitem(ap_loc): the "Archipelago Item" in tower shops (ap_loc 0..17) and locked chests (ap_loc 1000 + N)
// (obj_misc type 77; taking it goes through get_item -> ap_shop_item, which sends the check instead of adding it to the
// inventory). Its description (ap_desc) says what it holds, from the client's ap_scouts.txt ("offset|item|player|tag",
// line 1 = slot id); "" if unknown (generic description).
var it = instance_create(0, 0, obj_misc);
with (it)
{
    name = "Archipelago Item";
    type = 77;
    count = 1;
    weight = 0;
    sprite_index = spr_apicon;
    image_index = 0;
    dropped = spr_Dapicon;
    ap_loc = argument0;
    ap_desc = "";
}
var off = 250 + argument0;
if (argument0 >= 1000)
{
    off = 300 + argument0 - 1000;
}
if (file_exists("ap_scouts.txt"))
{
    var f = file_text_open_read("ap_scouts.txt");
    if (f != -1)
    {
        var sl = file_text_read_string(f);
        file_text_readln(f);
        if (sl == global.ap_slot_id && sl != "")
        {
            var pre = string(off) + "|";
            while (!file_text_eof(f))
            {
                var line = file_text_read_string(f);
                file_text_readln(f);
                if (string_pos(pre, line) == 1)
                {
                    var t = ap_field(line, 3);
                    it.ap_desc = ap_field(line, 1) + " for " + ap_field(line, 2);
                    if (t != "")
                    {
                        it.ap_desc += " (" + t + ")";
                    }
                    break;
                }
            }
        }
        file_text_close(f);
    }
}
return it;
