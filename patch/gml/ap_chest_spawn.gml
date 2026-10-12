// ap_chest_spawn(): called at the end of normal-floor generation (obj_dungeoncreator Step, player already at the start).
// Spawns the Archipelago chest next to the player's spawn point (0,0) on the first Descent floor (-1), and on any later floor
// that starts with received items still pending.
if (global.mode != 1 || global.level > -1 || global.ap_granted < 0)
{
    exit;
}
if (global.level != -1 && global.ap_granted >= global.ap_n)
{
    exit;
}
global.ap_chest_spawn = 1;
var c = instance_create(0, 0, obj_chest);
global.ap_chest_spawn = 0;
var found = 0;
with (c)
{
    for (var pass = 0; pass < 2 && !found; pass++)
    {
        for (var i = 0; i < 200; i++)
        {
            var ang = irandom(359);
            var dist = 26 + random(12);
            x = dist * dcos(ang);
            y = -dist * dsin(ang);
            if (place_free(x, y) && !place_meeting(x, y, obj_downstairs) && !place_meeting(x, y, obj_stairs) && !place_meeting(x, y, obj_trap) && !place_meeting(x, y, obj_player))
            {
                // strict pass: also demand some room around it so the player can walk up to it
                if (pass == 1 || (place_free(x + 10, y) && place_free(x - 10, y) && place_free(x, y + 10) && place_free(x, y - 10)))
                {
                    found = 1;
                    break;
                }
            }
        }
    }
    if (found)
    {
        image_angle = (90 * round(point_direction(x, y, 0, 0) / 90)) + 180; // lid/front toward the player
        audio_emitter_position(sound_emitter, x, y, 0);
    }
}
if (!found)
{
    with (c)
    {
        instance_destroy();
    }
    ap_emit("E|no free position for the Archipelago chest");
}
