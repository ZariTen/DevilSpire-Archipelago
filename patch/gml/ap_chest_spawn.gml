// ap_chest_spawn(): called from obj_dungeoncreator Step right after create_village(1) (the pre-tower camp, dungeon 0.5 / level 0.5;
// bonfire = obj_bonfire at (0,0), player spawns at (0,212), tower entrance at (0,-149)). Spawns the Archipelago chest at a FIXED spot
// next to the bonfire: first free candidate of a fixed list of offsets (deterministic; later ones only if decor/tombstones block).
if (global.mode != 1 || global.level != 0.5 || global.ap_granted < 0)
{
    exit;
}
var bx = 0;
var by = 0;
if (instance_exists(obj_bonfire))
{
    bx = obj_bonfire.x;
    by = obj_bonfire.y;
}
global.ap_chest_spawn = 1;
var c = instance_create(bx, by, obj_chest);
global.ap_chest_spawn = 0;
var found = 0;
with (c)
{
    var ox = bx;
    var oy = by;
    for (var pass = 0; pass < 2 && !found; pass++)
    {
        for (var i = 0; i < 12 && !found; i++)
        {
            switch (i)
            {
                case 0: cx = 40; cy = 16; break;
                case 1: cx = -40; cy = 16; break;
                case 2: cx = 40; cy = -16; break;
                case 3: cx = -40; cy = -16; break;
                case 4: cx = 0; cy = 44; break;
                case 5: cx = 56; cy = 0; break;
                case 6: cx = -56; cy = 0; break;
                case 7: cx = 0; cy = -44; break;
                case 8: cx = 56; cy = 32; break;
                case 9: cx = -56; cy = 32; break;
                case 10: cx = 72; cy = 16; break;
                default: cx = -72; cy = 16; break;
            }
            x = ox + cx;
            y = oy + cy;
            if (place_free(x, y) && !place_meeting(x, y, obj_bonfire) && !place_meeting(x, y, obj_entrance) && !place_meeting(x, y, obj_tombstone) && !place_meeting(x, y, obj_shade))
            {
                // strict pass: also demand some room around it so the player can walk up to it
                if (pass == 1 || (place_free(x + 10, y) && place_free(x - 10, y) && place_free(x, y + 10) && place_free(x, y - 10)))
                {
                    found = 1;
                }
            }
        }
    }
    if (found)
    {
        image_angle = (90 * round(point_direction(x, y, 0, 212) / 90)) + 180; // lid/front toward the player's arrival point
        audio_emitter_position(sound_emitter, x, y, 0);
    }
}
if (!found)
{
    with (c)
    {
        instance_destroy();
    }
    ap_emit("E|no free position for the Archipelago chest at the bonfire");
}
