# Devil Spire x Archipelago

A **fan-made, unofficial** [Archipelago](https://archipelago.gg) (multiworld randomizer) integration for the game **Devil Spire**.
It is **not affiliated with or endorsed by** the developer or publisher of Devil Spire or by the Archipelago project.
You **must own Devil Spire** yourself. This repository contains no game files; the patcher only contains the *differences* to your own `data.win`
and is published through GitHub Releases, not in git.

> Status: early version (0.1.0). The in-game part has not had real playtesting yet - expect bugs, back up your saves, and please report problems.

You only need to install two things: the **patcher** (changes your game, once) and the **apworld** (teaches Archipelago about Devil Spire).

## Quick start for PLAYERS
1. Download from the [GitHub Releases](../../releases) page: `devilspire_ap_patcher.exe` (Windows) or `devilspire_ap_patcher` (Linux), and `devilspire.apworld`.
2. Open your Devil Spire folder. In Steam: right-click *Devil Spire* > *Manage* > *Browse local files*. You should see `data.win` there.
3. Put the patcher file **in that folder** (next to `data.win`) and run it:
   - **Windows:** double-click `devilspire_ap_patcher.exe`. (If SmartScreen warns, choose *More info > Run anyway*.)
   - **Linux:** `cd` to the folder, then `chmod +x devilspire_ap_patcher && ./devilspire_ap_patcher`. This is correct even if you play with Proton: the patcher only edits a file.
   - It prints `SUCCESS`. It changes only `data.win` and saves your original as `data.win.orig`. You can delete the patcher afterwards (keep `data.win.orig`!).
4. Install the apworld: double-click `devilspire.apworld` (with Archipelago installed, version **0.6.8 or newer**), or copy it into Archipelago's `custom_worlds` folder.
5. Open the Archipelago Launcher and start **Devil Spire Client**. Connect it (`/connect host:port`, slot name, password if any) **before you start the game**.
6. Start Devil Spire (normally, through Steam) and choose *New Game*. The only mode is **Archipelago**. Received items are in the chest next to the camp bonfire.

Saves: Windows `%APPDATA%\Devil_Spire`; Linux/Proton `~/.local/share/Steam/steamapps/compatdata/<id>/pfx/drive_c/users/steamuser/AppData/Roaming/Devil_Spire`.
The client finds this folder by itself; if not, see the guides.

**Uninstall / go back to vanilla:** run the patcher again with `restore` (Windows: open a terminal in the folder and run `devilspire_ap_patcher.exe restore`; Linux: `./devilspire_ap_patcher restore`).
**After a Steam update** or "Verify integrity of game files", `data.win` is replaced by the original: just run the patcher again. If the patcher says the file is a different version, the game was updated - see Troubleshooting.

More detail: [docs/PLAYER_GUIDE.md](docs/PLAYER_GUIDE.md).

## Quick start for HOSTS
1. Everybody (host and players) installs `devilspire.apworld` (double-click it, or put it in Archipelago's `custom_worlds` folder). Archipelago **0.6.8+** is required.
2. Get the example options file [examples/DevilSpire.yaml](examples/DevilSpire.yaml), set `name:`, and adjust the options (explained in [docs/HOST_GUIDE.md](docs/HOST_GUIDE.md)):
   `death_link`, `floor_checks`, `trap_percentage`. Put one yaml per player in Archipelago's `Players` folder.
3. Run *Generate* in the Archipelago Launcher, then host the generated `.zip` (or upload to archipelago.gg - note that custom worlds only work on archipelago.gg if they are officially supported; otherwise host yourself).
4. Tell your players which **release version** to use. Host and players should use the same apworld `world_version` (this release: **0.1.0**, minimum Archipelago 0.6.8) and the patcher from the same release.

More detail: [docs/HOST_GUIDE.md](docs/HOST_GUIDE.md).

## Repository layout
`worlds-src/devilspire` apworld source - `client/` standalone client launcher - `patch/` game patch (UndertaleModCli script, GML, patcher source) - `docs/` guides and research notes - `examples/` example yaml.
Developer notes: [patch/README.md](patch/README.md), [TODO.md](TODO.md).

## License
Code in this repository is released under the [MIT License](LICENSE). Devil Spire and its assets belong to their respective owners and are not included.
