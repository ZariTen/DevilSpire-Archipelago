# Player guide (fan-made, unofficial; you need to own Devil Spire)

## 1. What you need
- Devil Spire installed through Steam, on Windows or Linux (Proton).
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.8 or newer.
- `devilspire.apworld` from this project's GitHub Releases (it contains the client and the game patch).
- The host's server address, your slot name, and (maybe) a password. Ask the host which release version they used.

Install the apworld: double-click `devilspire.apworld` while Archipelago is installed, or copy it into Archipelago's `custom_worlds` folder. Restart the Launcher. You should see **Devil Spire Client** in it.

## 2. Patch the game (once per apworld version)
1. Open the Launcher > **Devil Spire Client** and type `/auto_patch`.
   - It looks for Devil Spire in your Steam libraries. If it is not found, give the game folder: `/auto_patch D:\SteamLibrary\steamapps\common\Devil Spire` (Steam > right-click *Devil Spire* > *Manage* > *Browse local files* shows it).
2. Wait for `Patched. Start Devil Spire from Steam as usual`.

What it does: checks that `data.win` is exactly the supported original, saves it as `data.win.orig` (a valid backup is never overwritten), writes the patched file to a temporary file, checks it, and swaps it in. Nothing else is changed, nothing is downloaded or sent anywhere.
- `/patch_status` shows whether the game is original or patched and whether the backup is valid.
- Running `/auto_patch` again does nothing if the game is already patched with this version. After updating the apworld, run it again: an older patch is replaced automatically, starting from the backup. `/auto_patch force` re-patches from the backup.

## 3. Play
1. Open the Launcher > **Devil Spire Client**.
2. Type the server in the box at the top (e.g. `archipelago.gg:38281`) and connect, enter your slot name (and password). Wait until it says connected.
3. Start Devil Spire from Steam as usual (before or after the client: the game picks up the client's settings within a second). Checks you make while the client is closed or disconnected are sent when it reconnects.
4. Choose *New Game* and create a character. The only game mode is **Archipelago** (descend 100 floors; reaching floors and killing bosses are checks).
5. In the pre-tower camp, open the **chest next to the bonfire** (interact twice) to receive everything you were sent. Items that arrive mid-run wait until the chest is opened again or the next camp visit.
6. Each new run (after dying) re-grants your received items; checks you already found stay found.

Client commands (type in the client): `/auto_patch [game folder]` patches the game, `/patch_status` shows the patch state, `/restore` undoes the patch, `/savedir` shows or sets the save folder, `/apstatus` shows counters.

## 4. Saves
The patched game uses its **own** save folder `Devil_Spire_AP` (the normal game uses `Devil_Spire`), so your normal saves are never read or changed, and Archipelago characters do not mix with them.
- Windows: `%APPDATA%\Devil_Spire_AP` (paste into the Explorer address bar).
- Linux with Proton: `<Steam library>/steamapps/compatdata/1861290/pfx/drive_c/users/steamuser/AppData/Roaming/Devil_Spire_AP`.
The Archipelago files (`ap_in.txt`, `ap_out.txt`, `ap_config.ini`, ...) live in the same folder. The client finds it automatically (all Steam libraries); `/savedir` shows or overrides it.

### Starting over within the same multiworld
If you die, delete your character, or simply start a **New Game**, every item you received so far is granted again (once) at the camp chest. Checks you already found stay found. Large batches are handed out 100 items per chest opening ("more items waiting, open again").

### Warnings the client may show
- "data.win ... is NOT patched / older patch / unknown version": run `/auto_patch` (an unknown version usually means a game update: wait for an updated apworld).
- "The UNPATCHED Devil Spire is being played": the normal game is running (it saves to `Devil_Spire`). Close it, `/auto_patch`, start again.
- "patch protocol ...": the running game has an older patch; close it, `/auto_patch`, start again.
- "Steam Cloud manages ...": fine, but do not play the same seed on two PCs at once.
DeathLink only kills you during a run inside the tower; deaths that arrive on the title screen, in character creation or at the camp are ignored (not saved for later).

### Playing another multiworld
When you connect to a different multiworld (or slot), the client moves your Archipelago character and files to `Devil_Spire_AP/ap_backup/<date>_<old slot>/` (nothing is deleted) and starts clean: choose **New Game**. If the game was running at that moment it shows "different multiworld connected": quit and restart it. Reconnecting to the same multiworld never resets anything.

## 5. Uninstall
- Type `/restore` in the client: the backup `data.win.orig` is checked and put back as `data.win`, then the backup is removed.
- Or in Steam: right-click *Devil Spire* > *Properties* > *Installed Files* > *Verify integrity of game files*. This always restores the original (use it if `/restore` says the backup is missing or invalid). You can then delete `data.win.orig` and `ap_patch_info.json` from the game folder.
- Delete `devilspire.apworld` from `custom_worlds`. Delete `Devil_Spire_AP` if you no longer want your Archipelago saves.

## 6. Steam updates
Steam may replace the patched `data.win` when you verify files or when the game updates. If the game is no longer patched, run `/auto_patch` again. If the game got a **new version**, `/auto_patch` refuses (hash mismatch) until a new apworld supports it.

## 7. Troubleshooting
- **`/auto_patch`: "unsupported data.win" (hash mismatch):** your game build differs from the supported one (update, other store like itch/GOG, or an edited `data.win`). Nothing was changed. Verify files in Steam (*Properties* > *Installed Files* > *Verify integrity of game files*) and retry. If it still fails, report the sha256 it printed in an issue together with where you bought the game.
- **"already patched but data.win.orig is missing/invalid":** the backup is gone, so it cannot re-patch or restore. Verify files in Steam (restores the original), then run `/auto_patch` again.
- **"Devil Spire not found in any Steam library":** pass the game folder: `/auto_patch <folder>`.
- **Permission / file errors:** close the game first. Make sure the game folder is writable (Windows: Steam in `Program Files` may need the client run as administrator).
- **`/restore` says "probably a game update":** Steam replaced `data.win` with a new version; nothing was changed. Use *Verify integrity of game files*, then delete `data.win.orig` and `ap_patch_info.json`.
- **Non-ASCII user name (e.g. `C:\Users\José`):** the client handles it; whether this old GameMaker version can write its save folder there is untested. If your normal Devil Spire saves work, the Archipelago files should too (same mechanism).
- **Game does not start after patching:** `/restore` (or verify files in Steam), check that the game starts, then `/auto_patch` again. If it only fails when patched, report it with your Windows/Proton version.
- **Client can't find the save folder:** start the game once (and create a character) so the folder exists, then use `/savedir` in the client to see what it uses. To force a path: `/savedir C:\Users\You\AppData\Roaming\Devil_Spire_AP` (any path works), or start the client with `--savedir PATH`, or set the environment variable `DEVILSPIRE_SAVE_DIR`. On Linux look for the folder with `find ~ -type d -name Devil_Spire_AP 2>/dev/null`.
- **Items don't arrive:** is the client connected? open the camp chest (twice); check `/apstatus`.
- **Different Proton prefix than detected:** the client picks the newest `Devil_Spire_AP` folder; pass the right one with `/savedir`.
