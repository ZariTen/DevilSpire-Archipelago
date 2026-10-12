# Devil Spire Archipelago client (fan-made, unofficial)

Bridges the Archipelago server and the patched game through text files in the game's save dir (protocol: `patch/README.md`).
Code: `worlds-src/devilspire/ds_client.py` (CommonClient subclass) + `file_protocol.py` (pure file logic). It is registered
as the **"Devil Spire Client"** Launcher component by the apworld, and `client/DevilSpireClient.py` runs it standalone.
Targets Archipelago 0.6.8 (latest tag when written; API checked against it).

## Run
Launcher: install `devilspire.apworld` (or link `worlds/devilspire`), open the Launcher, click **Devil Spire Client**.
Standalone from any AP checkout with its requirements installed:
```
python client/DevilSpireClient.py --ap-root ~/Archipelago --connect host:38281 --name YourSlot [--password X] [--nogui] [--savedir DIR]
```
(`--ap-root` may be replaced by `$ARCHIPELAGO_ROOT`; the script also tries cwd/parents, `~/Archipelago`.)
**Start the client and let it connect BEFORE launching the game**: `ap_config.ini` (death_link, floor_check_step, base_id from slot_data) is read once at game start.

## Save dir
Priority: `--savedir` > `$DEVILSPIRE_SAVE_DIR` > auto-detect (`%APPDATA%\Devil_Spire`, Steam Proton prefixes
`~/.local/share/Steam/steamapps/compatdata/*/pfx/drive_c/users/*/AppData/Roaming/Devil_Spire` (also ~/.steam, Flatpak Steam); newest wins).
In the client: `/savedir [path]` shows/sets it, `/apstatus` shows counters.

## Behavior
- `ap_out.txt` is tailed by byte offset (only complete lines; truncated/deleted/empty file resets the offset; garbage lines ignored).
  `L|id` -> `LocationChecks` (deduped; ids unknown to the server are ignored with a warning), `G|1` -> `StatusUpdate` goal, `D|..` -> DeathLink Bounce (only for lines appearing while running, never replayed from history).
- `ap_in.txt` is rewritten atomically (tmp + `os.replace`) with the FULL received list in AP order (`I|idx|id|name|sender`, `items_handling=0b111`) plus the last 5 DeathLink events `D|seq|text` (seq is time based, strictly increasing).
- On reconnect: everything found is re-checked against the server's missing set and re-sent if needed; `ap_in.txt` is rewritten in full.
- First connect with a different seed/slot than the save dir last used (`ap_client_state.json`): `ap_out.txt` is cleared so stale checks from an old multiworld are not sent. Note `ap_granted.txt` (game-private) is not reset.

## Tests
- `python -m unittest discover client/tests` – protocol logic, no AP/server needed (16 tests).
- `python client/tests/e2e_local.py --ap-root <AP checkout> --python <venv python>` – generates a 2-player seed, runs a local MultiServer and two real clients with simulated `ap_out.txt` (15 checks: config, checks, item delivery, DeathLink, goal, truncation, reconnect). Needs `SKIP_REQUIREMENTS_UPDATE=1`-style headless venv (script sets it).
- apworld: symlink `worlds-src/devilspire` to `<AP>/worlds/devilspire`, `pytest worlds/devilspire` (46 pass).
Runtime with the real game is UNTESTED.
