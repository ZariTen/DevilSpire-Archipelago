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
    "ap_boss_cleared", "ap_goal", "ap_death_send", "ap_grant_item", "ap_poll" };

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
// poll every step from the persistent controller object
group.QueuePrepend(Data.Code.ByName("gml_Object_obj_god_Step_1"), "ap_poll();");

group.Import();
Console.WriteLine("AP patch applied.");
