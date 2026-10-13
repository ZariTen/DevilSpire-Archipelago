#!/usr/bin/env python3
"""Print the mod label drawn on the title screen, e.g. "Archipelago v0.1.0 (1a2b3c4)".
Version = world_version from worlds-src/devilspire/archipelago.json.
Id = first 7 hex of a sha256 over the patch sources (patch/ApPatch.csx, patch/gml/*.gml, patch/assets/*.png, patch/EXPECTED_ORIGINAL_SHA256),
so the same sources always give the same label (reproducible, independent of git state or commits).
"""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent


def patch_source_id() -> str:
    patch = root / "patch"
    files = [patch / "ApPatch.csx", patch / "EXPECTED_ORIGINAL_SHA256", *sorted((patch / "gml").glob("*.gml")),
             *sorted((patch / "assets").glob("*.png"))]
    h = hashlib.sha256()
    for f in files:
        h.update(f.relative_to(root).as_posix().encode() + b"\0")
        h.update(f.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    return h.hexdigest()[:7]


def mod_label() -> str:
    version = json.loads((root / "worlds-src/devilspire/archipelago.json").read_text())["world_version"]
    return f"Archipelago v{version} ({patch_source_id()})"


if __name__ == "__main__":
    print(mod_label())
