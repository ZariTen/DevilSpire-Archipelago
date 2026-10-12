# Player guide (fan-made, unofficial; you need to own Devil Spire)

## 1. What you need
- Devil Spire installed through Steam, on Windows or Linux (Proton).
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.8 or newer.
- `devilspire.apworld` from this project's GitHub Releases (it contains the client and the game patch).
- The host's server address, your slot name, and (maybe) a password. Ask the host which release version they used.

Install the apworld: double-click `devilspire.apworld` while Archipelago is installed, or copy it into Archipelago's `custom_worlds` folder. Restart the Launcher. You should see **Devil Spire Client** in it.

## 2. Make the patched copy (once per apworld version)
1. Open the Launcher > **Devil Spire Client** and type `/auto_patch`.
   - It looks for Devil Spire in your Steam libraries. If it is not found, give the game folder: `/auto_patch D:\SteamLibrary\steamapps\common\Devil Spire` (Steam > right-click *Devil Spire* > *Manage* > *Browse local files* shows it).
2. Wait for `Done. Patched game: ...`. The client prints the folder of the copy: `DevilSpire` inside your Archipelago folder (e.g. `C:\ProgramData\Archipelago\DevilSpire` on Windows, `~/Archipelago/DevilSpire` or next to your Archipelago install on Linux).
3. Add it to Steam: *Games* > *Add a Non-Steam Game to My Library* > *Browse*, select `Devil Spire.exe` in that folder, *Add Selected Programs*.
   - Linux: right-click the new entry > *Properties* > *Compatibility* > *Force the use of a specific Steam Play compatibility tool* > pick a Proton version.
   - Windows: the shortcut is optional; you can also run `Devil Spire.exe` from the copy directly.

What it does: checks that your `data.win` is exactly the supported original, copies the whole game folder, patches the copy's `data.win`, checks the result, and adds `steam_appid.txt` (needed to start the copy outside Steam's normal game entry). Your Steam install is only read, never changed, so the normal game keeps working. Running `/auto_patch` again replaces the copy (do this after updating the apworld).

## 3. Play
1. Open the Launcher > **Devil Spire Client**.
2. Type the server in the box at the top (e.g. `archipelago.gg:38281`) and connect, enter your slot name (and password). Wait until it says connected.
3. **Only now** start the patched copy (the non-Steam entry, not the normal Steam game). The game reads its Archipelago settings (DeathLink etc.) once when it starts; if you started it first, close it and start again.
4. Choose *New Game* and create a character. The only game mode is **Archipelago** (descend 100 floors; reaching floors and killing bosses are checks).
5. In the pre-tower camp, open the **chest next to the bonfire** (interact twice) to receive everything you were sent. Items that arrive mid-run wait until the chest is opened again or the next camp visit.
6. Each new run (after dying) re-grants your received items; checks you already found stay found.

Client commands (type in the client): `/auto_patch [game folder]` makes or refreshes the patched copy, `/savedir` shows or sets the save folder, `/apstatus` shows counters.

## 4. Saves
The game stores saves in `Devil_Spire`:
- Windows: `%APPDATA%\Devil_Spire` (paste into the Explorer address bar). The copy and the Steam game share it.
- Linux with Proton: `<Steam>/steamapps/compatdata/<number>/pfx/drive_c/users/steamuser/AppData/Roaming/Devil_Spire`. The non-Steam shortcut gets its own `<number>` (a new Proton prefix), so the copy starts with fresh saves, separate from the Steam game. The client picks the most recently used `Devil_Spire` folder.
The Archipelago files (`ap_in.txt`, `ap_out.txt`, `ap_config.ini`, ...) live in the same folder. Only your Archipelago character is shown in the continue list; other saves are hidden, not deleted.

## 5. Uninstall
Delete the `DevilSpire` folder inside your Archipelago folder, remove the non-Steam shortcut, and delete `devilspire.apworld` from `custom_worlds`. The Steam game was never modified.

## 6. Game updates
If Steam updates Devil Spire, `/auto_patch` refuses the new version (hash mismatch) until a new apworld supports it. Your existing patched copy keeps working.

## 7. Troubleshooting
- **`/auto_patch`: "unsupported data.win" (hash mismatch):** your game build differs from the supported one (update, other store like itch/GOG, or an edited `data.win`). Nothing was changed. Verify files in Steam (*Properties* > *Installed Files* > *Verify integrity*) and retry. If it still fails, report the sha256 it printed in an issue together with where you bought the game.
- **"already patched":** you pointed it at a patched copy. Give it the original Steam folder instead.
- **"Devil Spire not found in any Steam library":** pass the game folder: `/auto_patch <folder>`.
- **Permission or disk errors:** make sure the Archipelago folder is writable and has ~100 MB free. A failed run leaves the previous copy in place.
- **The copy exits right away:** start it from the non-Steam shortcut while Steam is running; `steam_appid.txt` must be next to `Devil Spire.exe` (run `/auto_patch` again to restore it). Linux: make sure a Proton version is forced for the shortcut.
- **Client can't find the save folder:** start the game once (and create a character) so the folder exists, then use `/savedir` in the client to see what it uses. To force a path: `/savedir C:\Users\You\AppData\Roaming\Devil_Spire` (any path works), or start the client with `--savedir PATH`, or set the environment variable `DEVILSPIRE_SAVE_DIR`. On Linux look for the folder with `find ~ -type d -name Devil_Spire 2>/dev/null`.
- **Items don't arrive:** is the client connected? did you start the client before the game? open the camp chest (twice); check `/apstatus`.
- **Different Proton prefix than detected:** the client picks the newest `Devil_Spire` folder; pass the right one with `/savedir`.
