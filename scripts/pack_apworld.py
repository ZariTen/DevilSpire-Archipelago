#!/usr/bin/env python3
"""Zip worlds-src/devilspire into build/devilspire.apworld the way the Launcher's "Build APWorlds" does:
archipelago.json gets "version"/"compatible_version" (APWorldContainer, container version 7) so Archipelago
reads it as a valid manifest. Skips __pycache__/*.pyc. Fails if the patch data is missing."""
import json
import zipfile
from pathlib import Path

CONTAINER_VERSION = 7  # worlds/Files.py container_version in Archipelago 0.6.x
root = Path(__file__).resolve().parent.parent
src = root / "worlds-src/devilspire"
out = root / "build/devilspire.apworld"
out.parent.mkdir(exist_ok=True)
manifest = json.loads((src / "archipelago.json").read_text())
manifest.update({"compatible_version": CONTAINER_VERSION, "version": CONTAINER_VERSION})
names = []
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for f in sorted(src.rglob("*")):
        rel = f.relative_to(src)
        if f.is_dir() or "__pycache__" in rel.parts or f.suffix == ".pyc" or rel.as_posix() == "archipelago.json":
            continue
        zf.write(f, Path("devilspire", rel).as_posix())
        names.append(rel.as_posix())
    zf.writestr("devilspire/archipelago.json", json.dumps(manifest))
if "data/devilspire.bsdiff4" not in names or "data/patch.json" not in names:
    out.unlink()
    raise SystemExit("patch data missing from apworld")
print(f"built {out}")
