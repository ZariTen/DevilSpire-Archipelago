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
ap_slot_check(ap_read_config());
if (!global.ap_stale && file_exists("ap_in.txt"))
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
                var idx = -1;
                if (string_length(si) > 0)
                {
                    idx = real(si);
                }
                // only the next new index is parsed further (cheap with hundreds of items); a complete item line
                // has 5 fields (I|idx|id|name|sender), truncated lines are ignored
                var sid = "";
                if (idx == global.ap_n && string_count("|", line) >= 4)
                {
                    sid = string_digits(ap_field(line, 2));
                }
                if (string_length(sid) > 0)
                {
                    if (idx == global.ap_n)
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
            // only kill during an active run inside the tower; never queued (title, character creation, camp,
            // tutorial, dead or no run => ignored)
            var inrun = 0;
            if (global.mode == 1 && room == rom_dungeon && global.level < 0 && global.ap_granted >= 0 && !global.ap_stale)
            {
                if (instance_exists(obj_player))
                {
                    if (obj_player.hp > 0 && obj_player.death == 0)
                    {
                        inrun = 1;
                    }
                }
            }
            if (global.ap_deathlink && inrun)
            {
                global.ap_dl_pending = 1;
                global.ap_dl_text = dtext;
            }
            else if (global.ap_deathlink)
            {
                ap_emit("X|deathlink ignored (no active run)");
            }
        }
    }
}
// run-state gated actions (Descent only, player alive in the dungeon)
if (!global.ap_stale && global.mode == 1 && room == rom_dungeon && instance_exists(obj_player))
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
        else if (global.ap_granted >= 0 && !instance_exists(obj_dungeoncreator))
        {
            // items: weightless ones are applied directly, weighted ones lie on the ground as normal pickups (ap_drop_spawn)
            if (global.ap_granted < global.ap_n)
            {
                ap_grant_pending();
                var direct = global.ap_cnt - global.ap_dcnt;
                if (global.level == 0.5 && global.ap_cnt > 0)
                {
                    // camp: persist the character together with ap_granted.txt (the game itself only saves on floor change),
                    // so quitting at the camp and choosing Continue neither loses nor re-grants these items
                    save_souls();
                    save_game(global.mode);
                    ap_save_granted();
                }
                if (global.ap_cnt > 0 && (global.level == 0.5 || global.ap_cnt > 3))
                {
                    with (instance_create(0, 0, obj_message))
                    {
                        text = "Archipelago: " + string(direct) + " received";
                        if (global.ap_dcnt > 0)
                        {
                            text += ", " + string(global.ap_dcnt) + " on the ground";
                        }
                    }
                }
            }
            ap_drop_spawn();
        }
    }
}
