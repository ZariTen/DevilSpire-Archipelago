# Player guide (fan-made, unofficial; you need to own Devil Spire)

## 1. What you need
- Devil Spire (Steam), Windows or Linux (Proton is fine).
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.8 or newer.
- From this project's GitHub Releases: the patcher (`devilspire_ap_patcher.exe` for Windows, `devilspire_ap_patcher` for Linux) and `devilspire.apworld`.
- The host's server address, your slot name, and (maybe) a password. Ask the host which release version they used.

## 2. Patch the game (once)
1. Steam > right-click *Devil Spire* > *Manage* > *Browse local files*. A folder with `data.win` and `Devil Spire.exe` opens.
2. Copy the patcher into this folder.
3. Windows: double-click `devilspire_ap_patcher.exe`. Linux: open a terminal in the folder and run `chmod +x devilspire_ap_patcher` once, then `./devilspire_ap_patcher`.
   Proton users: still run the **Linux** patcher natively (it just edits a file); no Wine needed.
4. Wait for `SUCCESS: data.win is patched`.

What it does: checks that `data.win` is exactly the supported original, copies it to `data.win.orig` (an existing backup is never overwritten), writes the patched file to a temporary file, and swaps it in. Nothing else in the folder is touched, and nothing is downloaded or sent anywhere.
Other commands: `status` (is it patched? is the backup valid?), `restore` (go back to the original), `help`.

## 3. Install the apworld
Double-click `devilspire.apworld` while Archipelago is installed, or copy it into Archipelago's `custom_worlds` folder. Restart the Launcher. You should see **Devil Spire Client** in it.

## 4. Play
1. Open the Launcher > **Devil Spire Client**.
2. Type the server in the box at the top (e.g. `archipelago.gg:38281`) and connect, enter your slot name (and password). Wait until it says connected.
3. **Only now** start Devil Spire. The game reads its Archipelago settings (DeathLink etc.) once when it starts; if you started it first, close it and start again.
4. Choose *New Game* and create a character. The only game mode is **Archipelago** (descend 100 floors; reaching floors and killing bosses are checks).
5. In the pre-tower camp, open the **chest next to the bonfire** (interact twice) to receive everything you were sent. Items that arrive mid-run wait until the chest is opened again or the next camp visit.
6. Each new run (after dying) re-grants your received items; checks you already found stay found.

Client commands (type in the client): `/savedir` shows or sets the save folder, `/apstatus` shows counters.

## 5. Saves
The game stores saves in `Devil_Spire`:
- Windows: `%APPDATA%\Devil_Spire` (paste into the Explorer address bar).
- Linux with Steam/Proton: `~/.local/share/Steam/steamapps/compatdata/<number>/pfx/drive_c/users/steamuser/AppData/Roaming/Devil_Spire` (also under `~/.steam/...` or the Flatpak Steam folder).
The Archipelago files (`ap_in.txt`, `ap_out.txt`, `ap_config.ini`, ...) live in the same folder. Only your Archipelago character is shown in the continue list; other saves are hidden, not deleted.

## 6. Uninstall
Run the patcher with `restore` (Windows: open `cmd` in the game folder, `devilspire_ap_patcher.exe restore`; Linux: `./devilspire_ap_patcher restore`). `data.win.orig` becomes `data.win` again. You can then delete the patcher.
Fallback: Steam > Properties > Installed Files > *Verify integrity of game files* restores the original.

## 7. Steam updates
Steam replaces a modified `data.win` when you verify files or when the game updates. If the game stops being patched, just run the patcher again. If the game got a **new version**, the patcher will refuse (hash mismatch) until a new release supports it.

## 8. Troubleshooting
- **Patcher: "not the version this patch was made for" (hash mismatch):** your game build differs from the supported one (update, other store like itch/GOG, or an edited `data.win`). Nothing was changed. Verify files in Steam and retry. If it still fails, report the "Found" hash in an issue together with where you bought the game. If `data.win.orig` exists and is valid, run `restore` first.
- **"Already patched":** nothing to do. Use `restore` to undo.
- **"data.win.orig already exists but is not the expected original":** the patcher never overwrites a backup. Move that file away yourself and run again.
- **"Permission denied":** close the game, make sure the folder is writable (Windows: avoid `Program Files`, or run as administrator).
- **Windows SmartScreen / antivirus warning:** the patcher is an unsigned program; check the SHA256 listed on the release page (`SHA256SUMS`), or build it yourself (see `patch/README.md`).
- **Game does not start after patching:** run `restore`, check the game starts, then patch again. If it only fails when patched, send the patcher output and your Proton/Windows version in an issue.
- **Client can't find the save folder:** start the game once (and create a character) so the folder exists, then use `/savedir` in the client to see what it uses. To force a path: `/savedir C:\Users\You\AppData\Roaming\Devil_Spire` (any path works), or start the client with `--savedir PATH`, or set the environment variable `DEVILSPIRE_SAVE_DIR`. On Linux look for the folder with `find ~ -type d -name Devil_Spire 2>/dev/null`.
- **Items don't arrive:** is the client connected? did you start the client before the game? open the camp chest (twice); check `/apstatus`.
- **Different Proton prefix than detected:** the client picks the newest `Devil_Spire` folder; pass the right one with `/savedir`.
