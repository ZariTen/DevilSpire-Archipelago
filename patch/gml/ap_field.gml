// ap_field(line, n): n-th (0-based) '|' separated field of line, "" if missing
var s = argument0;
var p;
repeat (argument1)
{
    p = string_pos("|", s);
    if (p == 0)
    {
        return "";
    }
    s = string_delete(s, 1, p);
}
p = string_pos("|", s);
if (p > 0)
{
    s = string_copy(s, 1, p - 1);
}
return s;
