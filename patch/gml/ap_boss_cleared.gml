// called when the last enemy of a boss floor died. Boss floors in Descent: -9,-19,...,-99 (-100 = Rhamdon = goal).
if (global.mode != 1 || global.level >= 0)
{
    exit;
}
var n = -global.level;
if (n >= 9 && n < 100 && (n mod 10) == 9)
{
    ap_emit("L|" + string(floor(global.ap_base + ((n - 9) / 10))));
}
