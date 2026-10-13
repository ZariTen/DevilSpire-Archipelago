// ap_copies(idx[, item_id]): how many copies of item_id (default: the item at idx) are among received items 0..idx (ap_in order)
var last = argument[0];
var want = -1;
if (argument_count > 1)
{
    want = argument[1];
}
else if (last >= 0)
{
    want = global.ap_item_id[last];
}
var c = 0;
for (var i = 0; i <= last; i++)
{
    if (global.ap_item_id[i] == want)
    {
        c += 1;
    }
}
return c;
