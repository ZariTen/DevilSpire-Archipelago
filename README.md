# Devil Spire x Archipelago

A **fan-made, unofficial** [Archipelago](https://archipelago.gg) (multiworld randomizer) add-on for **Devil Spire**.
Not affiliated with or endorsed by the game's developer/publisher or the Archipelago project.
You need your **own copy of Devil Spire on Steam**. No game files are included. Code is MIT licensed.

> Early version (0.1.0): not playtested in-game yet. Expect bugs and back up your saves.

## Players (Windows and Linux)
You need [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.8 or newer and Devil Spire installed through Steam.

1. **Install the apworld:** download `devilspire.apworld` from [Releases](../../releases) and double-click it (or copy it into Archipelago's `custom_worlds` folder).
2. **Patch the game (once):** open the Archipelago Launcher, start **Devil Spire Client**, and type `/auto_patch`.
   It finds Devil Spire in your Steam libraries (or use `/auto_patch <game folder>`), keeps a backup of the original `data.win` as `data.win.orig`, and patches the game.
3. **Connect:** in the Devil Spire Client, connect (server address, slot name, password). The game and the client can be started in any order.
4. **Play:** start Devil Spire from Steam as usual, choose *New Game*. Open the chest next to the bonfire in the camp to get your items.

The patched game keeps its saves in a separate `Devil_Spire_AP` folder, so your normal Devil Spire saves are never touched.

## Uninstall
- Type `/restore` in the Devil Spire Client (puts the original `data.win` back), **or** in Steam: right-click *Devil Spire* > *Properties* > *Installed Files* > *Verify integrity of game files*.
- Delete `devilspire.apworld`. Your Archipelago saves stay in `Devil_Spire_AP` until you delete them.

## Hosts
1. The host installs `devilspire.apworld` (needed to generate the game). Use Archipelago 0.6.8 or newer. Players of other games in the same multiworld do not need it.
2. Copy [examples/DevilSpire.yaml](examples/DevilSpire.yaml), set `name:`, and put one file per player in Archipelago's `Players` folder.
3. Click *Generate* in the Launcher, then host the `.zip` it makes.
4. Tell the Devil Spire players which release version to use (this one: 0.1.0). They only need the apworld (it contains the client and the game patch).

Details: [docs/HOST_GUIDE.md](docs/HOST_GUIDE.md).

## Problems?
- `/auto_patch` says the game is a different version: see [troubleshooting](docs/PLAYER_GUIDE.md#7-troubleshooting).
- The client warns about an unpatched or outdated game: run `/auto_patch` (after a Devil Spire update, wait for a new apworld).
- Items don't arrive: check the client is connected and open the chest (twice); see [the guide](docs/PLAYER_GUIDE.md#3-play).
- Client can't find your save folder: use `/savedir`, see [the guide](docs/PLAYER_GUIDE.md#4-saves).

Full guide: [docs/PLAYER_GUIDE.md](docs/PLAYER_GUIDE.md). Developers: [patch/README.md](patch/README.md), [TODO.md](TODO.md).

## License
[MIT](LICENSE). Devil Spire and its assets belong to their owners and are not included.
