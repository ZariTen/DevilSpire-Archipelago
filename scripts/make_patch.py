#!/usr/bin/env python3
"""Build the bsdiff4 patch shipped in the apworld: worlds-src/devilspire/data/{devilspire.bsdiff4,patch.json}.
  make_patch.py [pristine data.win] [patched data.win]   (default: game-copy/data.win, game-copy/data_patched.win)
Needs bsdiff4 (an Archipelago core requirement). The outputs are derived from game data and are git-ignored.
"""
import hashlib
import json
import sys
from pathlib import Path

import bsdiff4

root = Path(__file__).resolve().parent.parent
src = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "game-copy/data.win"
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else root / "game-copy/data_patched.win"
out = root / "worlds-src/devilspire/data"
expected = (root / "patch/EXPECTED_ORIGINAL_SHA256").read_text().strip()
a, b = src.read_bytes(), dst.read_bytes()
ha, hb = hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest()
if ha != expected:
    sys.exit(f"pristine {src} sha256 {ha} != expected {expected}")
known_path = root / "patch/KNOWN_PATCHED_SHA256"  # every released/built patched hash (for upgrade detection)
known = [l.strip() for l in known_path.read_text().splitlines() if l.strip()] if known_path.is_file() else []
if hb not in known:
    known.append(hb)
    known_path.write_text("\n".join(known) + "\n")
info = {"original_sha256": ha, "patched_sha256": hb, "known_patched_sha256": known}
info_path, patch_path = out / "patch.json", out / "devilspire.bsdiff4"
try:
    up_to_date = json.loads(info_path.read_text()) == info and patch_path.is_file()
except (OSError, ValueError):
    up_to_date = False
if not up_to_date:
    patch = bsdiff4.diff(a, b)
    if hashlib.sha256(bsdiff4.patch(a, patch)).digest() != hashlib.sha256(b).digest():
        sys.exit("self-check failed: patch does not reproduce the patched data.win")
    out.mkdir(parents=True, exist_ok=True)
    patch_path.write_bytes(patch)
    info_path.write_text(json.dumps(info, indent=1) + "\n")
print(f"patch {patch_path} ({patch_path.stat().st_size} bytes), {ha[:8]} -> {hb[:8]}")
