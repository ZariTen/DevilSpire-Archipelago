"""Devil Spire in-place patcher used by the client (`/auto_patch`, `/restore`, `/patch_status`). Fan-made, unofficial.

Patches the game's own data.win with the bsdiff4 patch shipped inside the apworld (data/devilspire.bsdiff4,
data/patch.json = {"original_sha256", "patched_sha256", "known_patched_sha256": [older builds]}).
Safety: the original is verified by sha256 and kept as data.win.orig (never overwritten once valid); the patched
file is written to data.win.ap-tmp, verified, fsynced and atomically renamed over data.win. Steam's "Verify
integrity of game files" also restores the original. No Archipelago imports (unit-testable).
"""
from __future__ import annotations

import hashlib
import json
import os
import pkgutil
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

STEAM_APP_ID = "1861290"
GAME_FOLDER = "Devil Spire"           # steamapps/common/<this>
PATCH_RESOURCE = "data/devilspire.bsdiff4"
PATCH_INFO_RESOURCE = "data/patch.json"
BACKUP = "data.win.orig"
TMP = "data.win.ap-tmp"
MARKER_FILE = "ap_patch_info.json"
STEAM_VERIFY_HINT = ("Steam > right-click Devil Spire > Properties > Installed Files > "
                     "Verify integrity of game files restores the original data.win.")


class PatchError(Exception):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------ Steam detection
def parse_libraryfolders(text: str) -> list[Path]:
    """Library paths from Steam's libraryfolders.vdf (both the old `"1" "path"` and the new `"path" "..."` form)."""
    out: list[Path] = []
    for key, val in re.findall(r'"([^"]+)"\s+"([^"]*)"', text):
        if key == "path" or key.isdigit() and ("/" in val or "\\" in val):
            p = Path(val.replace("\\\\", "\\"))
            if p not in out:
                out.append(p)
    return out


def steam_roots(env: Optional[Mapping[str, str]] = None, home: Optional[Path] = None,
                platform: Optional[str] = None) -> list[Path]:
    env = os.environ if env is None else env
    home = Path.home() if home is None else home
    platform = sys.platform if platform is None else platform
    if platform.startswith("win"):
        roots = [Path(env.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Steam",
                 Path(env.get("ProgramFiles", r"C:\Program Files")) / "Steam",
                 Path(r"C:\Steam")]
        try:  # registry (best effort)
            import winreg  # type: ignore
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                roots.insert(0, Path(winreg.QueryValueEx(k, "SteamPath")[0]))
        except Exception:
            pass
    else:
        roots = [home / ".local/share/Steam", home / ".steam/steam", home / ".steam/root",
                 home / ".var/app/com.valvesoftware.Steam/.local/share/Steam",
                 home / "Library/Application Support/Steam"]
    return roots


def steam_libraries(env=None, home=None, platform=None) -> list[Path]:
    libs: list[Path] = []
    for root in steam_roots(env, home, platform):
        for lib in [root, *_vdf_libs(root)]:
            if lib not in libs:
                libs.append(lib)
    return libs


def _vdf_libs(root: Path) -> list[Path]:
    for vdf in (root / "steamapps/libraryfolders.vdf", root / "config/libraryfolders.vdf"):
        try:
            return parse_libraryfolders(vdf.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    return []


def find_game_dir(env=None, home=None, platform=None) -> Optional[Path]:
    for lib in steam_libraries(env, home, platform):
        d = lib / "steamapps/common" / GAME_FOLDER
        if (d / "data.win").is_file():
            return d
    return None


# ------------------------------------------------------------------------------------------------ patch data
def _resource(name: str) -> Optional[bytes]:
    try:
        if __package__:
            return pkgutil.get_data(__package__, name)  # works inside the zipped .apworld too
        return (Path(__file__).parent / name).read_bytes()
    except (OSError, FileNotFoundError):
        return None


def load_patch() -> tuple[bytes, dict]:
    patch, info_raw = _resource(PATCH_RESOURCE), _resource(PATCH_INFO_RESOURCE)
    if not patch or not info_raw:
        raise PatchError("patch data missing from the apworld (rebuild it with scripts/build_apworld.sh)")
    return patch, json.loads(info_raw)


def apply_bsdiff(src: bytes, patch: bytes) -> bytes:
    try:
        import bsdiff4  # bundled with Archipelago (core requirement)
    except ImportError as e:
        raise PatchError("bsdiff4 is not available in this Archipelago install") from e
    return bsdiff4.patch(src, patch)


# ------------------------------------------------------------------------------------------------ status
@dataclass
class Status:
    game_dir: Path
    state: str            # "original" | "patched" | "outdated" | "unknown" | "missing"
    data_sha: Optional[str]
    backup: str           # "valid" | "missing" | "invalid"

    def describe(self) -> str:
        msg = {"original": "original (not patched)", "patched": "patched (current Archipelago version)",
               "outdated": "patched with an OLDER Archipelago version", "missing": "data.win missing",
               "unknown": f"unknown data.win (sha256 {self.data_sha})"}[self.state]
        return f"{self.game_dir}: {msg}; backup {BACKUP}: {self.backup}"


def _resolve_dir(game_dir: Optional[Path]) -> Path:
    if game_dir is None:
        game_dir = find_game_dir()
        if game_dir is None:
            raise PatchError("Devil Spire not found in any Steam library; pass the game folder, "
                             "e.g. /auto_patch <folder> (Steam > Manage > Browse local files shows it).")
    game_dir = Path(game_dir).expanduser()
    if not game_dir.is_dir():
        raise PatchError(f"not a folder: {game_dir}")
    return game_dir


def get_status(game_dir: Path, info: dict) -> Status:
    win, bak = game_dir / "data.win", game_dir / BACKUP
    sha = sha256_file(win) if win.is_file() else None
    known_old = set(info.get("known_patched_sha256", [])) - {info["patched_sha256"]}
    if sha is None:
        state = "missing"
    elif sha == info["original_sha256"]:
        state = "original"
    elif sha == info["patched_sha256"]:
        state = "patched"
    elif sha in known_old:
        state = "outdated"
    else:
        state = "unknown"
    backup = "missing" if not bak.is_file() else ("valid" if sha256_file(bak) == info["original_sha256"] else "invalid")
    return Status(game_dir, state, sha, backup)


def _atomic_write(path: Path, data: bytes) -> None:
    tmp = path.with_name(TMP)
    try:
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


# ------------------------------------------------------------------------------------------------ commands
def auto_patch(game_dir: Optional[Path] = None, patch: Optional[bytes] = None, info: Optional[dict] = None,
               force: bool = False, log: Callable[[str], None] = print) -> Status:
    """Patch data.win in place. Already current: nothing (force=True re-patches from the backup).
    Older AP build: re-patched from the valid backup. Unknown hash: refused."""
    if patch is None or info is None:
        patch, info = load_patch()
    game_dir = _resolve_dir(game_dir)
    st = get_status(game_dir, info)
    win, bak = game_dir / "data.win", game_dir / BACKUP
    log(st.describe())
    if st.state == "missing":
        raise PatchError(f"no data.win in {game_dir}")
    if st.state == "unknown":
        raise PatchError(f"unsupported data.win (sha256 {st.data_sha}, expected {info['original_sha256']}). "
                         "Nothing was changed. If Devil Spire was just updated on Steam, this apworld does not support "
                         "the new version yet: wait for an updated apworld (your normal game works as usual). "
                         f"Otherwise: {STEAM_VERIFY_HINT} Other game versions/stores are not supported.")
    if st.state == "patched" and not force:
        log("Already patched with this version. Nothing to do (use /auto_patch force to re-patch from the backup).")
        return st
    if st.state == "original":
        source = win.read_bytes()
        if st.backup == "valid":
            pass  # keep the existing good backup
        else:
            if st.backup == "invalid":  # never overwrite a file we cannot vouch for: keep it aside
                aside = game_dir / (BACKUP + ".invalid")
                os.replace(bak, aside)
                log(f"Existing {BACKUP} was not the original; moved it to {aside.name}.")
            _atomic_write(bak, source)
            if sha256_file(bak) != info["original_sha256"]:
                raise PatchError("writing the backup failed verification; nothing was patched")
            log(f"Backup saved: {bak}")
    else:  # patched (force) or outdated: start from the backup
        if st.backup != "valid":
            raise PatchError(f"data.win is already patched but {BACKUP} is {st.backup}, so it cannot be re-patched. "
                             + STEAM_VERIFY_HINT + " Then run /auto_patch again.")
        source = bak.read_bytes()
        log("Re-patching from the backup.")
    out = apply_bsdiff(source, patch)
    if hashlib.sha256(out).hexdigest() != info["patched_sha256"]:
        raise PatchError("patched result has the wrong checksum; data.win was not changed")
    _atomic_write(win, out)
    if sha256_file(win) != info["patched_sha256"]:
        raise PatchError("data.win verification after writing failed; run /restore or verify files in Steam")
    (game_dir / MARKER_FILE).write_text(json.dumps({k: info[k] for k in ("original_sha256", "patched_sha256")},
                                                   indent=1), encoding="utf-8")
    log("Patched. Start Devil Spire from Steam as usual (it uses its own save folder Devil_Spire_AP).")
    return get_status(game_dir, info)


def restore(game_dir: Optional[Path] = None, info: Optional[dict] = None,
            log: Callable[[str], None] = print) -> Status:
    """Put the verified backup back as data.win, then delete the backup and the marker."""
    if info is None:
        info = load_patch()[1]
    game_dir = _resolve_dir(game_dir)
    st = get_status(game_dir, info)
    win, bak = game_dir / "data.win", game_dir / BACKUP
    if st.state == "original":
        log(f"data.win is already the original. Nothing to restore.")
        if st.backup == "valid":
            bak.unlink()
        (game_dir / MARKER_FILE).unlink(missing_ok=True)
        return get_status(game_dir, info)
    if st.state in ("unknown", "missing"):
        # neither original nor one of our builds: most likely a game update replaced data.win; putting the old
        # backup back would downgrade/break the game
        raise PatchError(f"cannot restore: data.win is not a file this apworld made (sha256 {st.data_sha}); "
                         f"probably a game update. Nothing was changed. {STEAM_VERIFY_HINT} "
                         f"You can then delete {BACKUP} and {MARKER_FILE}.")
    if st.backup != "valid":
        raise PatchError(f"cannot restore: backup {BACKUP} is {st.backup}. {STEAM_VERIFY_HINT}")
    _atomic_write(win, bak.read_bytes())
    if sha256_file(win) != info["original_sha256"]:
        raise PatchError(f"restored data.win failed verification; backup kept. {STEAM_VERIFY_HINT}")
    bak.unlink()
    (game_dir / MARKER_FILE).unlink(missing_ok=True)
    log("Restored the original data.win and removed the backup.")
    return get_status(game_dir, info)


def patch_status(game_dir: Optional[Path] = None, info: Optional[dict] = None) -> Status:
    if info is None:
        info = load_patch()[1]
    return get_status(_resolve_dir(game_dir), info)
