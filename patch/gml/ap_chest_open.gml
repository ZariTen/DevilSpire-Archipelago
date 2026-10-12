// ap_chest_open(): called in the context of the Archipelago chest (from `interact`) when the opened chest is used.
if (global.ap_stale)
{
    with (instance_create(0, 0, obj_message))
    {
        text = "Archipelago: different multiworld connected. Quit and restart the game.";
    }
    exit;
}
if (global.ap_granted < 0)
{
    with (instance_create(0, 0, obj_message))
    {
        text = "Archipelago: no active run";
    }
    exit;
}
var pending = global.ap_n - global.ap_granted;
var done = ap_grant_pending();
if (global.ap_cnt > 0 && global.mode == 1 && global.level == 0.5)
{
    // persist the character together with ap_granted.txt so quitting at the camp and choosing Continue
    // neither loses nor re-grants these items (the game itself only saves on floor change)
    save_souls();
    save_game(global.mode);
}
audio_play_sound(snd_treasure, 1, false);
with (instance_create(0, 0, obj_message))
{
    if (pending <= 0)
    {
        text = "Archipelago: nothing new";
    }
    else if (global.ap_cnt == 1)
    {
        text = "Archipelago: received 1 item";
    }
    else
    {
        text = "Archipelago: received " + string(global.ap_cnt) + " items";
    }
}
if (done && global.ap_granted < global.ap_n)
{
    done = 0; // batch limit reached: keep the chest filled
    with (instance_create(0, 0, obj_message))
    {
        text = "Archipelago: more items waiting, open again";
    }
}
else if (!done)
{
    with (instance_create(0, 0, obj_message))
    {
        text = "Archipelago: some items could not be added, open again";
    }
}
else
{
    with (item)
    {
        instance_destroy();
    }
    item = -4; // empty chest; ap_poll re-arms it when new items arrive
}
