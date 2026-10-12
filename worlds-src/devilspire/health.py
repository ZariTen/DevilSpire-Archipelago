"""Setup health checks for the Devil Spire client (pure Python, no Archipelago imports). Fan-made, unofficial.

* data.win of the Steam install is not the current patched build (original after a Steam file check, older build)
* the game runs an unexpected patch protocol (S|<version> line in ap_out.txt)
* the UNPATCHED game is being played (activity in the original Devil_Spire save folder, which the patched game
  never touches)
* Steam Cloud manages the AP save folder (steam_autocloud.vdf): synced files from another PC could be stale
Each check returns a warning string or None; HealthMonitor only reports a warning when it changes.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Optional

ORIGINAL_SAVE_NAME = "Devil_Spire"
CLOUD_FILE = "steam_autocloud.vdf"


class DataWinCheck:
    """Status of data.win, re-hashed only when (mtime, size) of data.win / backup change."""

    def __init__(self, get_status: Callable[[Path], object]):
        self.get_status = get_status
        self._key = None
        self._status = None

    def check(self, game_dir: Optional[Path]) -> Optional[str]:
        if game_dir is None:
            return None
        key = [str(game_dir)]
        for n in ("data.win", "data.win.orig"):
            try:
                st = (Path(game_dir) / n).stat()
                key.append((st.st_mtime_ns, st.st_size))
            except OSError:
                key.append(None)
        if key != self._key:
            self._key, self._status = key, self.get_status(Path(game_dir))
        state = getattr(self._status, "state", None)
        if state == "patched" or state is None:
            return None
        why = {"original": "is NOT patched (a Steam file check or reinstall restores the original)",
               "outdated": "has an older Archipelago patch",
               "missing": "is missing",
               "unknown": "is not the supported version (Steam Verify restores it)"}[state]
        return f"Devil Spire's data.win in {game_dir} {why}. Run /auto_patch."


def protocol_warning(version: Optional[int], expected: int, label: Optional[str] = None,
                     expected_label: Optional[str] = None) -> Optional[str]:
    """Warns when the running game's S|<protocol>|<mod label> line does not match this apworld."""
    if label and expected_label and label != expected_label and (version is None or version == expected):
        return (f"The running game is {label}, this client is {expected_label}: "
                "close the game and run /auto_patch, then start it again.")
    if version is None or version == expected:
        return None
    return (f"The running game reports patch protocol {version}, this client expects {expected}: "
            "close the game and run /auto_patch, then start it again.")


class OriginalSaveWatch:
    """Notices writes in the original Devil_Spire folder (sibling of Devil_Spire_AP) after the client started."""

    def __init__(self):
        self._base: dict[str, float] = {}

    @staticmethod
    def _newest(d: Path) -> float:
        try:
            return max((f.stat().st_mtime for f in d.iterdir() if f.is_file()), default=0.0)
        except OSError:
            return 0.0

    def check(self, ap_save_dir: Optional[Path]) -> Optional[str]:
        if ap_save_dir is None:
            return None
        orig = Path(ap_save_dir).parent / ORIGINAL_SAVE_NAME
        now = self._newest(orig)
        base = self._base.setdefault(str(orig), now)
        if now > base:
            return (f"The UNPATCHED Devil Spire is being played (saves changed in {orig}). Archipelago needs the "
                    "patched game: close it, run /auto_patch, start it again.")
        return None


def cloud_warning(ap_save_dir: Optional[Path]) -> Optional[str]:
    if ap_save_dir is not None and (Path(ap_save_dir) / CLOUD_FILE).exists():
        return (f"Steam Cloud manages {ap_save_dir} ({CLOUD_FILE}). Archipelago state files are safe (they are "
                "tagged per multiworld; mismatching ones are reset), but avoid playing the same seed on two PCs.")
    return None


class HealthMonitor:
    def __init__(self, log: Callable[[str], None]):
        self.log = log
        self.last: dict[str, Optional[str]] = {}

    def report(self, key: str, msg: Optional[str]) -> None:
        if msg != self.last.get(key):
            self.last[key] = msg
            if msg:
                self.log(msg)
