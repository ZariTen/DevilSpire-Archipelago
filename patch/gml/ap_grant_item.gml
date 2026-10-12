// ap_grant_item(item_id): apply one received item to the live run. Returns 1 when handled, 0 to retry later.
var rel = argument0 - global.ap_base - 500;
var ok = 1;
if (rel == 0)
{
    global.ap_keys += 1; // Progressive Depth Key (floor gating itself not implemented yet)
}
else if (rel >= 1 && rel <= 9)
{
    global.ap_keys += 1; // individual key (tracked only as count for now)
}
else if (rel == 100)
{
    global.souls += 100;
    save_souls();
}
else if (rel == 101)
{
    var st = irandom(3);
    with (obj_player)
    {
        switch (st)
        {
            case 0:
                global.str += 3;
                physpow += (3 * attribute_multiplier(0));
                swingspd += (3 * attribute_multiplier(5));
                maxcarry += (3 * attribute_multiplier(10));
                break;
            case 1:
                global.int += 3;
                magipow += (3 * attribute_multiplier(1));
                maxmp += (3 * attribute_multiplier(3));
                mindres += (3 * attribute_multiplier(9));
                mp += (3 * attribute_multiplier(3));
                break;
            case 2:
                global.vit += 3;
                maxhp += (3 * attribute_multiplier(2));
                bodyres += (3 * attribute_multiplier(8));
                maxequip += (3 * attribute_multiplier(11));
                hp += (3 * attribute_multiplier(2));
                break;
            case 3:
                global.agi += 3;
                atkspd += (3 * attribute_multiplier(4));
                castspd += (3 * attribute_multiplier(6));
                movespd += (3 * attribute_multiplier(7));
                break;
        }
    }
}
else if (rel == 102 || rel == 103)
{
    var it;
    if (rel == 102)
    {
        it = generate_gold(100);
    }
    else
    {
        it = generate_stone(irandom(5));
    }
    global.ap_tmp = 1;
    with (obj_player)
    {
        if (!get_item(it))
        {
            global.ap_tmp = 0;
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
else if (rel >= 200 && rel <= 299)
{
    ok = 1; // traps: not implemented yet, skipped
}
else
{
    ap_emit("E|unknown item id " + string(argument0));
}
return ok;
