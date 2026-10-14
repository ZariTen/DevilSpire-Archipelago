// ap_force_difficulty(): Archipelago (Descent, mode 1) runs use the yaml difficulty (ap_config.ini "difficulty",
// default Extreme before the client wrote it). Called from the title (step + menu labels) and after load_game, so
// New Game and Continue both use it. Extreme/Nightmare count as unlocked (in memory only). Returns its name.
if (!variable_global_exists("ap_ready"))
{
    return "";
}
if (global.mode == 1)
{
    global.difficulty = clamp(round(global.ap_difficulty), 0, 4);
    if (global.difficulty >= 3)
    {
        global.extreme = 1;
    }
    if (global.difficulty >= 4)
    {
        global.nightmare = 1;
    }
}
switch (clamp(round(global.ap_difficulty), 0, 4))
{
    case 0:
        return "Easy";
    case 1:
        return "Normal";
    case 2:
        return "Hard";
    case 3:
        return "Extreme";
}
return "NIGHTMARE";
