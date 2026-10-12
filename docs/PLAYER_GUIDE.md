# Player guide

## What you need
- Devil Spire on Steam (Windows, or Linux with Proton).
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.8 or newer.
- `devilspire.apworld` from the project's Releases page.
- From your host: server address, slot name, and password (if any).

## Install
1. Double-click `devilspire.apworld`. (Or copy it into Archipelago's `custom_worlds` folder.)
2. Open the Archipelago Launcher and click **Devil Spire Client**.
3. Type `/auto_patch` and wait for "Patched".

`/auto_patch` finds the game in your Steam library. If it can't, give the folder:
`/auto_patch D:\SteamLibrary\steamapps\common\Devil Spire`.
It keeps a backup of the original file (`data.win.orig`).

## Play
1. In the client, connect to the server with your slot name.
2. Start Devil Spire from Steam as usual. (Client or game first, either is fine.)
3. Choose *New Game* and make a character. The only mode is **Archipelago**.
4. Open the chest next to the camp bonfire. Press interact twice to get your items.
5. Go down the tower. New floors and bosses count as checks.
6. Beat the boss on floor -100 to win.

Good to know:
- **Dying** starts a new run. Open the camp chest again to get all your items back.
- Items that arrive during a run wait in the camp chest until your next run.
- The chest gives up to 100 items at a time. If it says "open again", open it again.
- **DeathLink** (if on) only kills you inside the tower, never at the camp or in menus.
- Checks you make while the client is closed are sent when it reconnects.

## Saves
The patched game uses its own save folder, `Devil_Spire_AP`. Your normal saves are not touched.
- Windows: `%APPDATA%\Devil_Spire_AP`
- Linux: `<Steam library>/steamapps/compatdata/1861290/pfx/drive_c/users/steamuser/AppData/Roaming/Devil_Spire_AP`

If you join a **different multiworld**, the client moves your old Archipelago character to
`Devil_Spire_AP/ap_backup/` and you start fresh with *New Game*.

## Client commands
| Command | What it does |
|---|---|
| `/auto_patch` (or `/patch`) | Patch the game. Safe to run again. |
| `/restore` | Undo the patch. |
| `/status` | Show patch, save folder and connection state. |
| `/savedir [path]` | Show or set the save folder. Only needed if it isn't found. |

## Uninstall
1. Type `/restore` in the client. Or in Steam: right-click *Devil Spire* > *Properties* > *Installed Files* > *Verify integrity of game files*.
2. Delete `devilspire.apworld` from Archipelago's `custom_worlds` folder.
3. Optional: delete the `Devil_Spire_AP` save folder.

## Problems
- **"not patched" warning:** Steam's file check or a reinstall put the original back. Run `/auto_patch`.
- **"not the supported Steam version":** your `data.win` was changed or isn't the Steam version. Use Steam's *Verify integrity of game files*, then `/auto_patch`.
- **"different multiworld connected" in the game:** quit and restart the game, then choose *New Game*.
- **"UNPATCHED Devil Spire is being played":** close the game, run `/auto_patch`, start it again.
- **Which mod version do I have?** The title screen shows it in the top-left corner, e.g. `Archipelago v0.1.0 (6d49c01)`. `/status` shows the same text. If they differ, run `/auto_patch`.
- **Items don't arrive:** check the client is connected (`/status`). Then open the camp chest (interact twice).
- **Save folder not found:** start the game once, then check `/status`. Set it by hand with `/savedir <path>`.
- **Permission error:** close the game. On Windows, the client may need to run as administrator.
- **Non-English Windows user name** (e.g. `José`): not tested. If your normal saves work, this should too.
