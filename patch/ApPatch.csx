// Devil Spire x Archipelago patch.
//   UndertaleModCli load data.win -s ApPatch.csx -o data_patched.win
// Edits only the loaded data.win (use a COPY). GML for new helper scripts lives in ./gml/*.gml
using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UndertaleModLib.Compiler;
using UndertaleModLib.Models;
using UndertaleModLib.Util;

// mod label ("Archipelago v<world_version> (<patch source id>)"), set by apply_patch.sh; never hand-edited
string modLabel = Environment.GetEnvironmentVariable("DS_AP_MOD_LABEL") ?? "";
if (!Regex.IsMatch(modLabel, @"^Archipelago v[0-9A-Za-z.\-]+ \([0-9a-f]{7}\)$"))
    throw new Exception("DS_AP_MOD_LABEL missing or malformed (run patch/apply_patch.sh): '" + modLabel + "'");
string gmlDir = Path.Combine(Path.GetDirectoryName(ScriptPath), "gml");
string[] newScripts = { "ap_emit", "ap_field", "ap_save_granted", "ap_init", "ap_new_run", "ap_floor_reached",
    "ap_boss_cleared", "ap_goal", "ap_death_send", "ap_grant_item", "ap_poll",
    "ap_save_souls", "ap_read_config", "ap_slot_check", "ap_grant_pending", "ap_item_weighted", "ap_drop_make", "ap_drop_spawn", "ap_drop_taken", "ap_write_granted", "ap_leave_room", "ap_copies",
    "ap_save_checks", "ap_load_checks", "ap_lock_setup", "ap_shop_setup", "ap_make_apitem", "ap_shop_item", "ap_heartbeat" };

if (Data.Code.ByName("gml_Script_ap_emit") != null)
    throw new Exception("data.win already contains the AP patch. Start from the pristine copy.");

// (n) Archipelago item icon: new sprites spr_apicon (16x16 inventory icon) and spr_Dapicon (64x64, drawn in 3D on
// stands/the ground), each on its own new texture page, from patch/assets/*.png (patch/assets/make_ap_icon.py).
// Collision mask/bbox settings are copied from same-size vanilla item sprites (items never collide).
string assetDir = Path.Combine(Path.GetDirectoryName(ScriptPath), "assets");
void ImportSprite(string name, string png, string template)
{
    if (Data.Sprites.ByName(name) != null) throw new Exception("sprite exists: " + name);
    var tpl = Data.Sprites.ByName(template);
    byte[] bytes = File.ReadAllBytes(Path.Combine(assetDir, png));
    var img = GMImage.FromPng(bytes);
    if (img.Width != tpl.Width || img.Height != tpl.Height) throw new Exception(png + " must be " + tpl.Width + "x" + tpl.Height);
    var tex = new UndertaleEmbeddedTexture();
    tex.Scaled = tpl.Textures[0].Texture.TexturePage.Scaled;
    tex.TextureData.Image = img;
    Data.EmbeddedTextures.Add(tex);
    var tpi = new UndertaleTexturePageItem();
    tpi.SourceX = 0; tpi.SourceY = 0; tpi.SourceWidth = (ushort)img.Width; tpi.SourceHeight = (ushort)img.Height;
    tpi.TargetX = 0; tpi.TargetY = 0; tpi.TargetWidth = (ushort)img.Width; tpi.TargetHeight = (ushort)img.Height;
    tpi.BoundingWidth = (ushort)img.Width; tpi.BoundingHeight = (ushort)img.Height;
    tpi.TexturePage = tex;
    Data.TexturePageItems.Add(tpi);
    var spr = new UndertaleSprite();
    spr.Name = Data.Strings.MakeString(name);
    spr.Width = tpl.Width; spr.Height = tpl.Height;
    spr.MarginLeft = tpl.MarginLeft; spr.MarginRight = tpl.MarginRight; spr.MarginTop = tpl.MarginTop; spr.MarginBottom = tpl.MarginBottom;
    spr.OriginX = tpl.OriginX; spr.OriginY = tpl.OriginY;
    spr.BBoxMode = tpl.BBoxMode; spr.SepMasks = tpl.SepMasks; spr.Transparent = tpl.Transparent; spr.Smooth = tpl.Smooth; spr.Preload = tpl.Preload;
    spr.Textures.Add(new UndertaleSprite.TextureEntry() { Texture = tpi });
    spr.CollisionMasks.Add(tpl.CollisionMasks[0]);
    Data.Sprites.Add(spr);
    Console.WriteLine("imported sprite " + name + " (" + img.Width + "x" + img.Height + ")");
}
ImportSprite("spr_apicon", "ap_icon.png", "spr_misc");
ImportSprite("spr_Dapicon", "ap_icon_D.png", "spr_Dmisc");

var group = new CodeImportGroup(Data);
group.AutoCreateAssets = true;
group.ThrowOnNoOpFindReplace = true;

foreach (string n in newScripts)
    group.QueueReplace("gml_Script_" + n, File.ReadAllText(Path.Combine(gmlDir, n + ".gml")).Replace("@AP_MOD_LABEL@", modLabel));

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
// (a2) all difficulties selectable for free (no UNLOCK prices / locks on the mode screen)
Edit("gml_Object_obj_setup_Alarm_0", @"global\.extreme = ini_read_real\(""Unlockables"", ""Extreme"", 0\);",
     "global.extreme = 1;", "force Extreme unlocked");
Edit("gml_Object_obj_setup_Alarm_0", @"global\.nightmare = ini_read_real\(""Unlockables"", ""Nightmare"", 0\);",
     "global.nightmare = 1;", "force Nightmare unlocked");
// (b) boss floor cleared / floor reached
Edit("gml_Object_obj_enemy_Step_0", @"if \(aux\)(\s*)\{(\s*if \(global\.mode == 4\))",
     "if (aux)$1{\nap_boss_cleared();$2", "boss-floor clear hook");
Edit("gml_Script_next_floor", @"save_souls\(\);(\s*)save_game\(global\.mode\);",
     "ap_floor_reached();\nsave_souls();$1save_game(global.mode);\nap_save_granted();", "floor reached hook + commit AP run state with the save");
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

// (j) received WEIGHTED items lie on the ground as native obj_droppeditem pickups (ap_drop_spawn, called from ap_poll).
// ap_idx = ground key (received index*10 + armor part; -1 = vanilla drop); Destroy = picked up (room end does not fire Destroy) -> ap_drop_taken
group.QueuePrepend(Data.Code.ByName("gml_Object_obj_droppeditem_Create_0"), "ap_idx = -1;");
group.QueuePrepend(Data.Code.ByName("gml_Object_obj_droppeditem_Destroy_0"), "if (ap_idx >= 0)\n{\nap_drop_taken(ap_idx);\nap_idx = -1;\n}");

// (l) mod label: small, faint text in the top-left corner of the title screen (nothing else is drawn there).
// GMS1 has no font/align getters: colour+alpha are restored, align/font are left as this event normally ends
// (fnt_large, centered); buttons set their own font/align.
group.QueueAppend(Data.Code.ByName("gml_Object_obj_title_Draw_64"),
    "var ap_c = draw_get_colour();\nvar ap_a = draw_get_alpha();\n" +
    "draw_set_font(fnt_text);\ndraw_set_halign(fa_left);\ndraw_set_valign(fa_top);\ndraw_set_colour(c_white);\ndraw_set_alpha(0.45);\n" +
    "draw_text(16, 12, \"" + modLabel + "\");\n" +
    "if (variable_global_exists(\"ap_connected\"))\n{\nif (global.ap_connected)\n{\ndraw_text(16, 40, \"Connected: \" + global.ap_hb_name);\n}\nelse\n{\n" +
    "draw_set_alpha(0.95);\ndraw_set_colour(make_colour_rgb(255, 128, 48));\ndraw_text(16, 40, \"Client not connected\");\n}\n}\n" +
    "if (variable_global_exists(\"ap_stale\"))\n{\nif (global.ap_stale)\n{\ndraw_set_alpha(0.95);\ndraw_set_colour(make_colour_rgb(255, 128, 48));\ndraw_text(16, 68, \"New seed connected - finish/quit the run to switch\");\n}\n}\n" +
    "draw_set_alpha(ap_a);\ndraw_set_colour(ap_c);\ndraw_set_halign(fa_center);\ndraw_set_valign(fa_middle);\ndraw_set_font(fnt_large);");

// (m) "Archipelago" subtitle under the title logo (main page only, once the burn-in reveal is complete):
// fnt_large, logo orange #FFBF7F, centred at (960, 628) between the logo (ends y=588) and the first button (y=744)
Edit("gml_Object_obj_logo_Draw_64", @"(draw_sprite_part_ext\(spr_title, [^;]*\);)",
     "$1\nif (appear == 114)\n{\ndraw_set_font(fnt_large);\ndraw_set_halign(fa_center);\ndraw_set_valign(fa_middle);\n" +
     "draw_set_colour(make_colour_rgb(255, 191, 127));\ndraw_text(960, 628, \"Archipelago\");\ndraw_set_colour(c_white);\n}",
     "Archipelago subtitle under the logo");

// leaving the camp forfeits untaken camp ground items (before next_floor changes global.level)
group.QueuePrepend(Data.Code.ByName("gml_Script_next_floor"), "ap_leave_room();");

// (o) locked chest checks: one locked chest per eligible floor holds the Archipelago Item (ap_lock_setup, right before
// the player is created at the end of normal floor generation); shop checks: 2 stands on shop floors
Edit("gml_Object_obj_dungeoncreator_Step_0",
     @"(with \(instance_create\(0, 0, obj_player\)\)\s*\{\s*mode = other\.mode;\s*dungeon = other\.dungeon;\s*level = other\.level;\s*tip = other\.tip;\s*facing = other\.image_angle \+ 180;)",
     "ap_lock_setup();\n$1", "AP locked chest");
group.QueuePrepend(Data.Code.ByName("gml_Object_obj_shop_Create_0"), "ap_shop = -1;");
Edit("gml_Object_obj_dungeoncreator_Step_0", @"instance_create\(x \+ 40, y \+ 20, obj_shop\);", "instance_create(x + 40, y + 20, obj_shop);\nap_shop_setup();", "AP shop stands");
group.QueuePrepend(Data.Code.ByName("gml_Script_get_item"),
    "if (instance_exists(argument0))\n{\nif (argument0.object_index == obj_misc)\n{\nif (argument0.type == 77)\n{\nreturn ap_shop_item(argument0);\n}\n}\n}");
group.QueuePrepend(Data.Code.ByName("gml_Script_get_item_description"),
    "if (instance_exists(argument0))\n{\nif (argument0.object_index == obj_misc)\n{\nif (argument0.type == 77)\n{\nif (argument0.ap_desc != \"\")\n{\nreturn argument0.ap_desc;\n}\nreturn \"Sends an Archipelago check to the multiworld.\";\n}\n}\n}");

// poll every step from the persistent controller object
group.QueuePrepend(Data.Code.ByName("gml_Object_obj_god_Step_1"), "ap_poll();");

group.Import();

// (k) separate save folder: with UseAppDataSaveLocation the GMS1 runner saves to %APPDATA%\<GEN8 Name>
// (Proton: compatdata/<id>/pfx/drive_c/users/steamuser/AppData/Roaming/<Name>). Original Name is "Devil_Spire";
// the patched game uses "Devil_Spire_AP" so it never reads or writes the normal saves.
if (Data.GeneralInfo.Name.Content != "Devil_Spire")
    throw new Exception("unexpected GEN8 Name " + Data.GeneralInfo.Name.Content);
Data.GeneralInfo.Name = Data.Strings.MakeString("Devil_Spire_AP");
Console.WriteLine("AP patch applied.");
