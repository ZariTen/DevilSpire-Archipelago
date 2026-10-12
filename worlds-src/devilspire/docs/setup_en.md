# Devil Spire Setup Guide (fan-made, unofficial, early version)

## Requirements
- A legitimate copy of Devil Spire (no game files are ever distributed).
- Archipelago 0.6.8 or newer.
- `devilspire.apworld` (double-click to install, or put it in Archipelago's `custom_worlds` folder).
- Devil Spire installed through Steam (Windows, or Linux with Proton).

## Patching the game
Open the Launcher, start **Devil Spire Client** and type `/auto_patch` (or `/auto_patch <game folder>` if Steam is not found).
It backs up the original `data.win` as `data.win.orig` and patches the game in place; launch it from Steam as usual.
The patched game saves to its own `Devil_Spire_AP` folder (your normal saves are untouched).
To undo: `/restore` in the client, or Steam's *Verify integrity of game files*. `/status` shows the current state.

## Generating a game
1. Create a YAML (Launcher "Generate Template Options", or the example yaml in the repository).
2. Put it in `Players/`, run Generate, host the result.

## Playing
1. Open the Launcher and start **Devil Spire Client**; connect to the server.
2. Start the game from Steam (before or after the client), choose New Game, and open the chest next to the camp bonfire to receive items.
Each new run re-grants all received items. Full guide: docs/PLAYER_GUIDE.md in the repository.
