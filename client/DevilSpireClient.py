#!/usr/bin/env python3
"""Standalone launcher for the Devil Spire Archipelago client (fan-made, unofficial).

Needs an Archipelago source checkout/install (CommonClient.py + its pip requirements) - found via, in order:
  --ap-root <dir>, $ARCHIPELAGO_ROOT, the current dir and its parents, ~/Archipelago, ~/.cache/ap-src.
Everything else (--connect, --name, --password, --nogui, --savedir, archipelago:// url) is passed to the client.
The client code itself lives in worlds-src/devilspire/ds_client.py (shared with the apworld's Launcher component).
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORLD_DIR = HERE.parent / "worlds-src" / "devilspire"


def find_ap_root(argv):
    cands = []
    if "--ap-root" in argv:
        i = argv.index("--ap-root")
        cands.append(Path(argv[i + 1]))
        del argv[i:i + 2]
    if os.environ.get("ARCHIPELAGO_ROOT"):
        cands.append(Path(os.environ["ARCHIPELAGO_ROOT"]))
    cwd = Path.cwd()
    cands += [cwd, *cwd.parents, Path.home() / "Archipelago", Path.home() / ".cache" / "ap-src"]
    for c in cands:
        if (c / "CommonClient.py").is_file():
            return c
    return None


def main():
    argv = sys.argv[1:]
    root = find_ap_root(argv)
    if root is None:
        sys.exit("Archipelago not found: pass --ap-root <dir> or set ARCHIPELAGO_ROOT (dir containing CommonClient.py).")
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(WORLD_DIR))
    import ds_client
    ds_client.launch(*argv)


if __name__ == "__main__":
    main()
