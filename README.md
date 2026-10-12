# Devil Spire x Archipelago

A **fan-made, unofficial** [Archipelago](https://archipelago.gg) (multiworld randomizer) add-on for **Devil Spire**.
Not affiliated with or endorsed by the game's developer/publisher or the Archipelago project.
You need your **own copy of Devil Spire on Steam**. No game files are included. Code is MIT licensed.

> Early version (0.1.0): not playtested in-game yet. Expect bugs and back up your saves.

## Players (Windows and Linux)
You need [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.8 or newer.

1. **Download** from [Releases](../../releases): `devilspire.apworld` and the patcher (`devilspire_ap_patcher.exe` for Windows, `devilspire_ap_patcher` for Linux).
2. **Patch the game.** In Steam: right-click *Devil Spire* > *Manage* > *Browse local files*. Put the patcher there, next to `data.win`, and run it.
   - Windows: double-click it.
   - Linux: `chmod +x devilspire_ap_patcher && ./devilspire_ap_patcher` (also for Proton).
   - Wait for `SUCCESS`.
3. **Install the apworld:** double-click `devilspire.apworld` (or copy it into Archipelago's `custom_worlds` folder).
4. **Connect first:** open the Archipelago Launcher, start **Devil Spire Client**, and connect (server address, slot name, password). Do this **before** starting the game.
5. **Play:** start Devil Spire, choose *New Game*. Open the chest next to the bonfire in the camp to get your items.

## Uninstall
- Run the patcher with `restore` (`devilspire_ap_patcher.exe restore` on Windows, `./devilspire_ap_patcher restore` on Linux) to get the original game back.
- Delete `devilspire.apworld`.

## Hosts
1. The host installs `devilspire.apworld` (needed to generate the game). Use Archipelago 0.6.8 or newer. Players of other games in the same multiworld do not need it.
2. Copy [examples/DevilSpire.yaml](examples/DevilSpire.yaml), set `name:`, and put one file per player in Archipelago's `Players` folder.
3. Click *Generate* in the Launcher, then host the `.zip` it makes.
4. Tell the Devil Spire players which release version to use (this one: 0.1.0). They need the patcher and the apworld (for the client).

Details: [docs/HOST_GUIDE.md](docs/HOST_GUIDE.md).

## Problems?
- Patcher says the game is a different version: see [troubleshooting](docs/PLAYER_GUIDE.md#8-troubleshooting).
- Items don't arrive: start the client before the game and open the chest (twice); see [the guide](docs/PLAYER_GUIDE.md#4-play).
- Client can't find your save folder: use `/savedir`, see [the guide](docs/PLAYER_GUIDE.md#5-saves).

Full guide: [docs/PLAYER_GUIDE.md](docs/PLAYER_GUIDE.md). Developers: [patch/README.md](patch/README.md), [TODO.md](TODO.md).

## License
[MIT](LICENSE). Devil Spire and its assets belong to their owners and are not included.
