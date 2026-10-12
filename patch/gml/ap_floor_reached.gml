// called from next_floor after global.level changed. Emits "Reach Floor -N" check per floor_check_step.
if (global.mode != 1 || global.level >= 0)
{
    exit;
}
var n = -global.level;
if (global.ap_floor_step > 0 && ((n - 1) mod global.ap_floor_step) == 0)
{
    ap_emit("L|" + string(floor(global.ap_base + 100 + (n - 1))));
}
