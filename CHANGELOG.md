# Changelog

## v0.1.0

First public test version of the Devil Spire world for [Archipelago](https://archipelago.gg). Pre-release: expect bugs.

**What it is:** an Archipelago add-on for Devil Spire. One mode, **Archipelago** (Descent, 100 floors down).
Checks are bosses, every 2nd floor, one locked chest per floor and 2 shop items on floors -10 to -90.
Beat the boss on floor -100 to win. The client patches your own game with `/auto_patch`.

**Requirements**
- Archipelago 0.6.8 or newer.
- Your own Steam copy of Devil Spire (Windows, or Linux with Proton).

**Install** (details in the [player guide](https://github.com/ZariTen/DevilSpire-Archipelago/blob/main/docs/PLAYER_GUIDE.md))
1. Double-click `devilspire.apworld` (or copy it into Archipelago's `custom_worlds` folder).
2. In the Archipelago Launcher, open **Devil Spire Client** and type `/auto_patch`.
3. Connect the client, then start Devil Spire from Steam and choose *New Game*.

`DevilSpire.yaml` is an example player yaml (see the [host guide](https://github.com/ZariTen/DevilSpire-Archipelago/blob/main/docs/HOST_GUIDE.md)).

**Not yet tested**
- Windows (`/auto_patch`, `/restore`, saves) is untested; developed and tested on Linux with Proton.
- A full run to floor -100 is still pending; a partial 2-player run went smoothly.

**Fan project:** unofficial, not affiliated with or endorsed by the Devil Spire developer or the Archipelago team.
No game files are included; the patch only changes your own copy, locally. The MIT license covers only this project's own code.
