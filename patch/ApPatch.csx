// Devil Spire x Archipelago patch.
//   UndertaleModCli load data.win -s ApPatch.csx -o data_patched.win
// Edits only the loaded data.win (use a COPY). GML for new helper scripts lives in ./gml/*.gml
using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UndertaleModLib.Compiler;
using UndertaleModLib.Models;

string gmlDir = Path.Combine(Path.GetDirectoryName(ScriptPath), "gml");
string[] newScripts = { "ap_emit", "ap_field", "ap_save_granted", "ap_init", "ap_new_run", "ap_floor_reached",
    "ap_boss_cleared", "ap_goal", "ap_death_send", "ap_grant_item", "ap_poll",
    "ap_save_souls", "ap_grant_pending", "ap_chest_open", "ap_chest_spawn", "ap_chest_init" };

if (Data.Code.ByName("gml_Script_ap_emit") != null)
    throw new Exception("data.win already contains the AP patch. Start from the pristine copy.");

var group = new CodeImportGroup(Data);
group.AutoCreateAssets = true;
group.ThrowOnNoOpFindReplace = true;

foreach (string n in newScripts)
    group.QueueReplace("gml_Script_" + n, File.ReadAllText(Path.Combine(gmlDir, n + ".gml")));

void Edit(string codeName, string pattern, string replacement, string what)
{
    var code = Data.Code.ByName(codeName);
    if (code == null) throw new Exception("missing code entry " + codeName);
    string text = GetDecompiledText(code);
    int count = Regex.Matches(text, pattern, RegexOptions.Singleline).Count;
    if (count != 1) throw new Exception($"{what}: pattern matched {count} times in {codeName}");
    group.QueueRegexFindReplace(code, pattern, replacement, true);
    Console.WriteLine("queued " + codeName + " : " + what);
}

// (a) force-unlock Descent; AP init (config + state) at startup
Edit("gml_Object_obj_setup_Alarm_0", @"global\.descent = ini_read_real\(""Unlockables"", ""Descent"", 0\);",
     "global.descent = 1;", "force Descent unlocked");
Edit("gml_Object_obj_setup_Alarm_0", @"load_souls\(\);", "load_souls();\nap_init();", "ap_init at startup");
// (b) boss floor cleared / floor reached
Edit("gml_Object_obj_enemy_Step_0", @"if \(aux\)(\s*)\{(\s*if \(global\.mode == 4\))",
     "if (aux)$1{\nap_boss_cleared();$2", "boss-floor clear hook");
Edit("gml_Script_next_floor", @"save_souls\(\);(\s*)save_game\(global\.mode\);",
     "ap_floor_reached();\nsave_souls();$1save_game(global.mode);", "floor reached hook");
// (c) goal
Edit("gml_Object_obj_rhamdon_Step_1", @"room = rom_ending;", "ap_goal();\nroom = rom_ending;", "goal hook");
// (d) death (DeathLink send); receive+items are handled in ap_poll
Edit("gml_Object_obj_player_Step_0", @"death = 1;(\s*)if \(global\.mode != 4\)",
     "death = 1;\nap_death_send();$1if (global.mode != 4)", "death hook");
// (e) new run => re-apply all received items
Edit("gml_Object_obj_charcreation_Alarm_0", @"save_game\(mode\);(\s*)audio_stop_all\(\);(\s*)room = rom_dungeon;",
     "ap_new_run(mode);\nsave_game(mode);$1audio_stop_all();$2room = rom_dungeon;", "new run hook");
// ---- Single game mode: "Archipelago" (= internal Descent, global.mode == 1) ----
// (f) mode starts as Descent; the title Step forces it every step on the mode-select screen
Edit("gml_Object_obj_setup_Alarm_0", @"global\.mode = 0;", "global.mode = 1;", "default mode = Descent");
Edit("gml_Object_obj_title_Step_0", @"menu_cursor\(0\);", "menu_cursor(0);\nif (screen == 1)\n{\n    global.mode = 1;\n}", "force mode 1 on mode select");
// (g) mode button: fixed text, no arrows, inert (action 0 matches no case) and greyed out
Edit("gml_Script_buttonize_title", @"else(\s*)\{(\s*)var modus;", "else$1{\nglobal.mode = 1;$2var modus;", "force mode in buttonize");
Edit("gml_Script_buttonize_title", @"text = modus;(\s*)action = 1;(\s*)master = 36;(\s*)leftnright = 1;",
     "text = \"Archipelago\";$1action = 0;$2master = 36;$3nulled = 1;", "single inert Archipelago mode button");
// (h) Continue screen: only the Descent (Archipelago) save is listed
Edit("gml_Script_buttonize_title", @"!file_exists\(""ascent_character\.ini""\) && !file_exists\(""descent_character\.ini""\) && !file_exists\(""chaos_character\.ini""\) && !file_exists\(""arena_character\.ini""\) && !file_exists\(""soul_character\.ini""\) && !file_exists\(""immortal_character\.ini""\)",
     "!file_exists(\"descent_character.ini\")", "Continue only checks Descent save");
Edit("gml_Script_buttonize_title", @"var as = file_exists\(""ascent_character\.ini""\);", "var as = 0;", "hide ascent save");
Edit("gml_Script_buttonize_title", @"var ch = file_exists\(""chaos_character\.ini""\);", "var ch = 0;", "hide chaos save");
Edit("gml_Script_buttonize_title", @"var ar = file_exists\(""arena_character\.ini""\);", "var ar = 0;", "hide arena save");
Edit("gml_Script_buttonize_title", @"var so = file_exists\(""soul_character\.ini""\);", "var so = 0;", "hide soul save");
Edit("gml_Script_buttonize_title", @"var im = file_exists\(""immortal_character\.ini""\);", "var im = 0;", "hide immortal save");
// (i) player-visible renames Descent -> Archipelago
Edit("gml_Script_buttonize_title", @"""Descent \(entrance\)""", "\"Archipelago (entrance)\"", "rename continue label");
Edit("gml_Script_buttonize_title", @"""Descent \(flr\. """, "\"Archipelago (flr. \"", "rename continue label 2");
Edit("gml_Script_mode_difficulty_floor", @"modus = ""Descent"";", "modus = \"Archipelago\";", "HUD/gameover/ending mode name");
Edit("gml_Object_obj_title_Draw_64", @"""Climb Down#Floors: 99#Dungeons: 10#Ending T""", "\"Archipelago#Floors: 99#Dungeons: 10#Ending T\"", "mode description");

// (j) Archipelago chest: obj_chest Create uses ap_chest_init() instead of the loot roll when global.ap_chest_spawn is set
group.QueuePrepend(Data.Code.ByName("gml_Object_obj_chest_Create_0"),
    "ap_chest = 0;\nif (global.ap_chest_spawn)\n{\nap_chest_init();\nexit;\n}");
// using an OPENED Archipelago chest grants the pending items instead of the (placeholder) item
Edit("gml_Script_interact", @"else if \(open == 90\)(\s*)\{(\s*)if \(argument0 == 0 \|\| other\.monster\)",
     "else if (open == 90)$1{\nif (ap_chest)\n{\nap_chest_open();\nexit;\n}$2if (argument0 == 0 || other.monster)", "AP chest open");
// spawn it in the pre-tower camp (village, dungeon 0.5) next to the bonfire, right after create_village(1)
Edit("gml_Object_obj_dungeoncreator_Step_0", @"create_village\(1\);", "create_village(1);\nap_chest_spawn();", "AP chest spawn (camp)");

// poll every step from the persistent controller object
group.QueuePrepend(Data.Code.ByName("gml_Object_obj_god_Step_1"), "ap_poll();");

group.Import();
Console.WriteLine("AP patch applied.");
