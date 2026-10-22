# Player guide

Unofficial fan project: you need your own Steam copy of Devil Spire, and the patch only changes that copy.

## 1. What you need
- Devil Spire on Steam (Windows, or Linux with Proton).
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.8 or newer.
- `devilspire.apworld` from the project's Releases page.
- From your host: server address, slot name, and password (if any).

## 2. Install
1. Double-click `devilspire.apworld` (or copy it into Archipelago's `custom_worlds` folder).
2. Open the Archipelago Launcher and click **Devil Spire Client**.

## 3. Patch the game
Type `/auto_patch` in the client and wait for "Patched".
- It finds the game in your Steam library. If not, give the folder:
  `/auto_patch D:\SteamLibrary\steamapps\common\Devil Spire`
- It keeps a backup of the original file (`data.win.orig`). Running it again is safe.
- The title screen shows the mod version in the top-left corner, e.g. `Archipelago v0.1.0 (e183280)`.

## 4. Connect
1. In the client, connect to the server with your slot name.
2. Start Devil Spire from Steam.
3. Under the version, the title shows `Connected: <slot>`. If it says **Client not connected**, connect first.

Connect before you choose *New Game*. You can play without the client, but you get no items until it has connected.

## 5. Play
1. Choose *New Game* and make a character. The only mode is **Archipelago**.
   The difficulty is set by your host's yaml and can't be changed in game (it shows e.g. `Extreme (AP)`).
2. At the camp you get your items:
   - Stat boosts, gold, stones, souls and spells go straight to you.
   - Equipment, rings and potions lie on the ground around you. Pick up what you want.
3. Go down the tower. These are checks:
   - every boss (floors -9, -19, ... -99)
   - every 2nd floor (the host can change this)
   - one **locked chest** per floor (its key is somewhere on the floor; not on boss or shop floors)
   - the **Archipelago Item** (orb icon, 150 gold) on 2 shop stands on floors -10, -20, ... -90
4. Beat the boss on floor -100 to win.

Good to know:
- An Archipelago Item's description shows what it holds and who gets it, e.g. `Progressive Weapon for Alex (progression)`.
- When you find another player's item, a message shows `Sent <item> to <player>`.
- **Dying** starts a new run. You get all your items again at the camp. Checks you already sent don't come back.
- Gear is **progressive**: each Progressive Weapon, Armor (full set), Shield or Accessory is a better tier. A new run gives
  your best tier. Each Progressive Spellbook gives a new spell (Basic, then Advanced, then Master).
- Items that arrive during a run come at once. Equipment drops at your feet.
- Camp items you leave on the ground stay behind when you enter the tower. You get them again next run.
- At most 60 items lie on the ground at once. Pick some up and the rest appear.
- **DeathLink** (if on) only kills you inside the tower.
- Checks you make while the client is closed are sent when it reconnects.

### Saves
The patched game uses its own save folder, `Devil_Spire_AP`. Your normal saves are not touched.
- Windows: `%APPDATA%\Devil_Spire_AP`
- Linux: `<Steam library>/steamapps/compatdata/1861290/pfx/drive_c/users/steamuser/AppData/Roaming/Devil_Spire_AP`

### New seed
If you connect to a **different multiworld**, the client moves your old Archipelago files to `Devil_Spire_AP/ap_backup/`.
- On the title or at the camp, the game switches to the new seed at once. Choose *New Game*.
- During a run in the tower, that run sends nothing. Die or quit to the title; the game then switches by itself.

### Client commands
| Command | What it does |
|---|---|
| `/auto_patch` (or `/patch`) | Patch the game. Safe to run again. |
| `/restore` | Undo the patch. |
| `/status` | Show patch, save folder and connection state. |
| `/savedir [path]` | Show or set the save folder. Only needed if it isn't found. |

## 6. Undo
1. Type `/restore` in the client. Or in Steam: right-click *Devil Spire* -> *Properties* -> *Installed Files* ->
   *Verify integrity of game files*.
2. Delete `devilspire.apworld` from Archipelago's `custom_worlds` folder.
3. Optional: delete the `Devil_Spire_AP` save folder.

## 7. Problems
| Message or problem | Fix |
|---|---|
| "not patched" | Steam's file check or a reinstall put the original back. Run `/auto_patch`. |
| "not the supported Steam version" | Use Steam's *Verify integrity of game files*, then `/auto_patch`. |
| "UNPATCHED Devil Spire is being played" | Close the game, run `/auto_patch`, start it again. |
| Title says "Client not connected" | Start the client and connect. No items are given until it has connected. |
| "New seed connected - finish/quit the run to switch" | See [New seed](#new-seed). |
| Items don't arrive | Check `/status`. Items come in the camp or the tower, not in menus. |
| Mod version differs from `/status` | Run `/auto_patch`. |
| Save folder not found | Start the game once, then `/status`. Set it with `/savedir <path>`. |
| Permission error | Close the game. On Windows, try running the client as administrator. |
| Non-English Windows user name | Not tested. If your normal saves work, this should too. |
