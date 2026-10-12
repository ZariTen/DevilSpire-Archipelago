// ap_grant_item(item_id): apply one received item to the live run (docs/item-catalog.md). Returns 1 when handled, 0 to retry later.
// Item id = ap_base + 500 + code. Items are re-granted on every new run when the Archipelago chest is opened (ap_granted reset by ap_new_run; souls only once per slot); traps only fire
// when they were received live (global.ap_live[global.ap_cur], set by ap_poll) and are then consumed.
var rel = argument0 - global.ap_base - 500;
var ok = 1;
var it = -4;
if (rel >= 100 && rel <= 103)
{
    // stat orbs: same effect as the game's red orb (+3 to one stat), applied directly to the live player
    var st = rel - 100; // 0 STR, 1 INT, 2 VIT, 3 AGI
    with (obj_player)
    {
        switch (st)
        {
            case 0:
                global.str += 3;
                physpow += (3 * attribute_multiplier(0));
                swingspd += (3 * attribute_multiplier(5));
                maxcarry += (3 * attribute_multiplier(10));
                if (global.str >= 40)
                {
                    steam_give_achievement("ach_TheBarbarian");
                }
                break;
            case 1:
                global.int += 3;
                magipow += (3 * attribute_multiplier(1));
                maxmp += (3 * attribute_multiplier(3));
                mindres += (3 * attribute_multiplier(9));
                mp += (3 * attribute_multiplier(3));
                if (global.int >= 40)
                {
                    steam_give_achievement("ach_TheSorcerer");
                }
                break;
            case 2:
                global.vit += 3;
                maxhp += (3 * attribute_multiplier(2));
                bodyres += (3 * attribute_multiplier(8));
                maxequip += (3 * attribute_multiplier(11));
                hp += (3 * attribute_multiplier(2));
                if (global.vit >= 40)
                {
                    steam_give_achievement("ach_TheWarrior");
                }
                break;
            case 3:
                global.agi += 3;
                atkspd += (3 * attribute_multiplier(4));
                castspd += (3 * attribute_multiplier(6));
                movespd += (3 * attribute_multiplier(7));
                if (global.agi >= 40)
                {
                    steam_give_achievement("ach_TheRogue");
                }
                break;
        }
    }
}
else if (rel == 104)
{
    global.statpoints += 1; // unspent point, spent in the character sheet like a level-up point
}
else if (rel == 113)
{
    // souls persist in the vault across deaths: grant only the first time this received item index is applied
    if (global.ap_cur > global.ap_souls_max)
    {
        global.souls += 100;
        save_souls();
        global.ap_souls_max = global.ap_cur;
        ap_save_souls();
    }
}
else if (rel == 110)
{
    it = generate_gold(irandom_range(150, 450)); // like the boss yellow orb
}
else if (rel == 111)
{
    it = generate_gold(1000);
}
else if (rel == 112)
{
    it = generate_stone(irandom(35)); // like the boss blue orb (stone kinds 0-35)
}
else if (rel == 120 || rel == 121 || rel == 122)
{
    if (rel == 120)
    {
        it = generate_potion(0); // Red Potion
    }
    else if (rel == 121)
    {
        it = generate_potion(25); // Blue Potion
    }
    else
    {
        it = generate_potion(99); // White Potion
    }
    if (rel != 122)
    {
        with (it)
        {
            count = 3;
            weight = 0.75;
        }
    }
}
else if (rel == 130)
{
    it = generate_spell(irandom_range(0, 11));
}
else if (rel == 131)
{
    it = generate_spell(irandom_range(12, 23));
}
else if (rel == 132)
{
    it = generate_spell(irandom_range(24, 47));
}
else if (rel >= 140 && rel <= 148)
{
    var cat = floor((rel - 140) / 3); // 0 weapon, 1 armor, 2 accessory
    var lv = 25 * (((rel - 140) mod 3) + 1);
    if (cat == 0)
    {
        it = generate_weapon(lv, (random(3) < 1) + (2 * irandom(11))); // same type roll as generate_equipment
    }
    else if (cat == 1)
    {
        it = generate_armor(lv, irandom(3));
    }
    else
    {
        it = generate_accessory(lv, irandom(3));
    }
}
else if (rel == 149 || rel == 150)
{
    it = generate_shield(25 * (rel - 148));
}
else if (rel == 151)
{
    it = generate_ring(irandom(35));
}
else if (rel >= 200 && rel <= 202)
{
    if (global.ap_live[global.ap_cur])
    {
        global.ap_live[global.ap_cur] = 0;
        if (rel == 200)
        {
            // Ambush: 3-5 floor-appropriate enemies (obj_enemy Create picks the dungeon's monsters)
            var n = 3 + irandom(2);
            with (obj_player)
            {
                repeat (n)
                {
                    with (instance_create(x + random_range(-48, 48), y + random_range(-48, 48), obj_enemy))
                    {
                        if (!place_free(x, y))
                        {
                            instance_destroy();
                        }
                        else
                        {
                            alerted = 1800;
                        }
                    }
                }
            }
        }
        else if (rel == 201)
        {
            // Plague: one body ailment + one mind ailment (like a purple potion, twice)
            var b = irandom(3);
            var m = irandom(3);
            with (obj_player)
            {
                switch (b)
                {
                    case 0: poison += (600 / bodyres); break;
                    case 1: cramp += (600 / bodyres); break;
                    case 2: root += (600 / bodyres); break;
                    case 3: paralysis += (600 / bodyres); break;
                }
                switch (m)
                {
                    case 0: headache += (600 / mindres); break;
                    case 1: mute += (600 / mindres); break;
                    case 2: blind += (600 / mindres); break;
                    case 3: confusion += (600 / mindres); break;
                }
            }
        }
        else
        {
            // Pickpocket: lose half of all carried gold (moneybags and gold stacks)
            for (var i = 0; i < 100; i++)
            {
                var g = global.inventory[i];
                if (instance_exists(g))
                {
                    if (g.object_index == obj_misc && (g.type == 1 || g.type == 15))
                    {
                        var lost = floor(g.count / 2);
                        if (lost > 0)
                        {
                            g.count -= lost;
                            if (g.type == 1)
                            {
                                g.weight = g.count * 0.01;
                                g.image_index = floor((g.count - 1) / 25);
                                obj_player.carrying -= (lost * 0.01);
                            }
                        }
                    }
                }
            }
        }
        with (instance_create(0, 0, obj_message))
        {
            text = "Archipelago: trap!";
        }
    }
}
else
{
    ap_emit("E|unknown item id " + string(argument0));
}
if (instance_exists(it))
{
    // spells go to the grimoire (get_item); everything else is added to the inventory without the encumbrance check
    global.ap_tmp = 0;
    if (it.object_index == obj_spell)
    {
        with (obj_player)
        {
            global.ap_tmp = get_item(it);
        }
    }
    else
    {
        with (obj_player)
        {
            global.ap_tmp = (add_inventory(it, -4, 0) == 1);
        }
    }
    if (!global.ap_tmp)
    {
        with (it)
        {
            instance_destroy();
        }
        ok = 0;
    }
}
return ok;
