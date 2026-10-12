# Devil Spire x Archipelago

A **fan-made, unofficial** [Archipelago](https://archipelago.gg) (multiworld randomizer) add-on for **Devil Spire**.
Not affiliated with or endorsed by the game's developer/publisher or the Archipelago project.
You need your **own copy of Devil Spire on Steam**. No game files are included. Code is MIT licensed.

> Early version (0.1.0): not playtested in-game yet. Expect bugs and back up your saves.

## Players (Windows and Linux)
You need [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.8 or newer and Devil Spire installed through Steam.

1. **Install the apworld:** download `devilspire.apworld` from [Releases](../../releases) and double-click it (or copy it into Archipelago's `custom_worlds` folder).
2. **Make the patched copy (once):** open the Archipelago Launcher, start **Devil Spire Client**, and type `/auto_patch`.
   It finds Devil Spire in your Steam libraries (or use `/auto_patch <game folder>`), copies the game into Archipelago's `DevilSpire` folder and patches the copy. Your Steam install is not changed.
3. **Add the copy to Steam:** *Games* > *Add a Non-Steam Game* > *Browse*, pick `Devil Spire.exe` in the folder the client printed.
   - Linux: right-click the new entry > *Properties* > *Compatibility* > force a Proton version.
   - Windows: you can also just run that `Devil Spire.exe` directly.
4. **Connect first:** in the Devil Spire Client, connect (server address, slot name, password) **before** starting the game.
5. **Play:** start the patched copy, choose *New Game*. Open the chest next to the bonfire in the camp to get your items.

## Uninstall
Delete the `DevilSpire` folder inside your Archipelago folder, the non-Steam shortcut, and `devilspire.apworld`. The Steam game was never modified.

## Hosts
1. The host installs `devilspire.apworld` (needed to generate the game). Use Archipelago 0.6.8 or newer. Players of other games in the same multiworld do not need it.
2. Copy [examples/DevilSpire.yaml](examples/DevilSpire.yaml), set `name:`, and put one file per player in Archipelago's `Players` folder.
3. Click *Generate* in the Launcher, then host the `.zip` it makes.
4. Tell the Devil Spire players which release version to use (this one: 0.1.0). They only need the apworld (it contains the client and the game patch).

Details: [docs/HOST_GUIDE.md](docs/HOST_GUIDE.md).

## Problems?
- `/auto_patch` says the game is a different version: see [troubleshooting](docs/PLAYER_GUIDE.md#7-troubleshooting).
- Items don't arrive: start the client before the game and open the chest (twice); see [the guide](docs/PLAYER_GUIDE.md#3-play).
- Client can't find your save folder: use `/savedir`, see [the guide](docs/PLAYER_GUIDE.md#4-saves).

Full guide: [docs/PLAYER_GUIDE.md](docs/PLAYER_GUIDE.md). Developers: [patch/README.md](patch/README.md), [TODO.md](TODO.md).

## License
[MIT](LICENSE). Devil Spire and its assets belong to their owners and are not included.
