// ap_lock_setup(): end of Descent floor generation (obj_dungeoncreator, right before the player is created).
// On eligible floors -N (N = 1..98, not a boss floor N mod 10 = 9, not a shop floor N mod 10 = 0) whose
// "Locked Chest Floor -N" check is unsent, one locked chest holds the "Archipelago Item" (picked up -> ap_shop_item).
// Vanilla rolls a locked chest (plus its key) for only ~1 in 10 chests, so if there is none, one chest is made locked
// and gets a key exactly as obj_chest Create does; if the floor has no usable chest at all, one is placed in a room.
if (global.mode != 1 || global.ap_stale || global.level >= 0)
{
    exit;
}
var n = -global.level;
if (n < 1 || n > 98 || (n mod 10) == 9 || (n mod 10) == 0)
{
    exit;
}
if (string_char_at(global.ap_lock_sent, n) == "1")
{
    exit;
}
var c = -4;
with (obj_chest)
{
    if (c == -4 && locked == 1)
    {
        c = id;
    }
}
if (c == -4)
{
    with (obj_chest)
    {
        if (c == -4 && open == 0 && instance_exists(item))
        {
            if (item.object_index != obj_skullcrab)
            {
                c = id;
            }
        }
    }
    if (c == -4)
    {
        var r = -4;
        var k = 0;
        with (obj_room)
        {
            if ((x != 0 || y != 0) && !place_meeting(x, y, obj_stairs))
            {
                k += 1;
                if (irandom(k - 1) == 0)
                {
                    r = id;
                }
            }
        }
        if (r == -4)
        {
            exit;
        }
        c = instance_create(r.x, r.y, obj_chest);
    }
    if (c.locked != 1)
    {
        with (c)
        {
            locked = 1;
            texF = background_get_texture(tex_chestF2);
            texS = background_get_texture(tex_chestS2);
            texT = background_get_texture(tex_chestT2);
            texL = background_get_texture(tex_chestL2);
            texH = background_get_texture(tex_chestH2);
            with (instance_create(0, 0, obj_key))
            {
                item = generate_key();
                aux1 = irandom(instance_number(obj_cell) - 1);
                aux2 = 0;
                var cwidth = 0;
                var cheight = 0;
                with (obj_cell)
                {
                    if (other.aux2 == other.aux1)
                    {
                        other.aux1 = id;
                    }
                    else
                    {
                        other.aux2++;
                    }
                    cwidth = (sprite_width / 2) - 4;
                    cheight = (sprite_height / 2) - 4;
                }
                x = aux1.x + random_range(-cwidth, cwidth);
                y = aux1.y + random_range(-cheight, cheight);
                while (!place_free(x, y) || point_distance(x, y, instance_nearest(x, y, obj_chest).x, instance_nearest(x, y, obj_chest).y) < 32)
                {
                    x = aux1.x + random_range(-cwidth, cwidth);
                    y = aux1.y + random_range(-cheight, cheight);
                }
            }
        }
    }
}
with (c)
{
    if (instance_exists(item))
    {
        with (item)
        {
            instance_destroy();
        }
    }
    item = ap_make_apitem(1000 + n);
}
