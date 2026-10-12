// polled every step from obj_god Step 1; does real work every ap_poll_frames frames.
if (!variable_global_exists("ap_ready"))
{
    exit;
}
global.ap_tick += 1;
if (global.ap_tick < global.ap_poll_frames)
{
    exit;
}
global.ap_tick = 0;
if (file_exists("ap_in.txt"))
{
    var f = file_text_open_read("ap_in.txt");
    if (f != -1)
    {
        var maxd = 0;
        var dtext = "";
        var announced = 0;
        while (!file_text_eof(f))
        {
            var line = file_text_read_string(f);
            file_text_readln(f);
            var kind = string_char_at(line, 1);
            if (kind == "I")
            {
                var si = string_digits(ap_field(line, 1));
                var sid = string_digits(ap_field(line, 2));
                if (string_length(si) > 0 && string_length(sid) > 0)
                {
                    var idx = real(si);
                    if (idx >= global.ap_n && idx == global.ap_n)
                    {
                        global.ap_item_id[idx] = real(sid);
                        global.ap_item_name[idx] = ap_field(line, 3);
                        global.ap_live[idx] = global.ap_loaded; // received while playing (traps only fire for live items)
                        global.ap_n = idx + 1;
                        if (global.ap_loaded && announced < 3)
                        {
                            announced += 1;
                            with (instance_create(0, 0, obj_message))
                            {
                                text = "Archipelago: " + global.ap_item_name[idx];
                            }
                        }
                    }
                }
            }
            else if (kind == "D")
            {
                var sd = string_digits(ap_field(line, 1));
                if (string_length(sd) > 0)
                {
                    if (real(sd) > maxd)
                    {
                        maxd = real(sd);
                        dtext = ap_field(line, 2);
                    }
                }
            }
        }
        file_text_close(f);
        global.ap_loaded = 1;
        if (!global.ap_dl_init)
        {
            global.ap_dl_init = 1;
            global.ap_dl_seq = maxd;
        }
        else if (maxd > global.ap_dl_seq)
        {
            global.ap_dl_seq = maxd;
            if (global.ap_deathlink)
            {
                global.ap_dl_pending = 1;
                global.ap_dl_text = dtext;
            }
        }
    }
}
// run-state gated actions (Descent only, player alive in the dungeon)
if (global.mode == 1 && room == rom_dungeon && instance_exists(obj_player))
{
    if (obj_player.hp > 0 && obj_player.death == 0)
    {
        if (global.ap_dl_pending)
        {
            global.ap_dl_pending = 0;
            global.ap_dl_recv = 1;
            with (instance_create(0, 0, obj_message))
            {
                text = "DeathLink: " + global.ap_dl_text;
            }
            obj_player.hp = 0;
        }
        else if (global.ap_granted >= 0 && global.ap_granted < global.ap_n)
        {
            var cnt = 0;
            var changed = 0;
            while (global.ap_granted < global.ap_n && cnt < 8)
            {
                global.ap_cur = global.ap_granted;
                if (ap_grant_item(global.ap_item_id[global.ap_granted]))
                {
                    global.ap_fail = 0;
                    global.ap_granted += 1;
                    cnt += 1;
                    changed = 1;
                }
                else
                {
                    global.ap_fail += 1;
                    if (global.ap_fail >= 5)
                    {
                        global.ap_fail = 0;
                        global.ap_granted += 1; // give up on an ungrantable item (e.g. inventory full)
                        changed = 1;
                        ap_emit("E|skipped item idx " + string(global.ap_granted - 1));
                    }
                    break;
                }
            }
            if (changed)
            {
                ap_save_granted();
            }
        }
    }
}
