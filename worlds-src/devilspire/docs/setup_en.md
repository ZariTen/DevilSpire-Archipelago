# Devil Spire Setup Guide (fan-made, unofficial, early version)

## Requirements
- A legitimate copy of Devil Spire (no game files are ever distributed).
- Archipelago 0.6.8 or newer.
- `devilspire.apworld` (double-click to install, or put it in Archipelago's `custom_worlds` folder).
- The Devil Spire patcher from the project's GitHub Releases (`devilspire_ap_patcher.exe` on Windows, `devilspire_ap_patcher` on Linux).

## Patching the game
Put the patcher in the Devil Spire folder (Steam: right-click > Manage > Browse local files), next to `data.win`, and run it.
It backs up `data.win` as `data.win.orig` and patches `data.win`. Run it with `restore` to undo.

## Generating a game
1. Create a YAML (Launcher "Generate Template Options", or the example yaml in the repository).
2. Put it in `Players/`, run Generate, host the result.

## Playing
1. Open the Launcher and start **Devil Spire Client**; connect to the server.
2. Only then start the game, choose New Game, and open the chest next to the camp bonfire to receive items.
Each new run re-grants all received items. Full guide: docs/PLAYER_GUIDE.md in the repository.
