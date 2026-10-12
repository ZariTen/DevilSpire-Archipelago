# Devil Spire client (developers)

The client ships inside the apworld as the **Devil Spire Client** Launcher component.
Code: `worlds-src/devilspire/` (`ds_client.py`, `file_protocol.py`, `auto_patch.py`, `health.py`).
File protocol: [docs/dev/patch.md](../docs/dev/patch.md).

## Run without the Launcher
```
python client/DevilSpireClient.py --ap-root <Archipelago source> --connect host:38281 --name Slot [--nogui] [--savedir DIR]
```

## Tests
- Unit tests: `python -m unittest discover client/tests`
- End-to-end (local server, real client, simulated game):
  `python client/tests/e2e_local.py --ap-root <AP> --python <venv python>` and `client/tests/e2e_robustness.py` (same args).
- World tests: link `worlds-src/devilspire` to `<AP>/worlds/devilspire`, then `pytest worlds/devilspire`.
