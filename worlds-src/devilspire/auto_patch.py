"""Devil Spire auto-patcher (same approach as Archipelago's Undertale client). Fan-made, unofficial.

`/auto_patch [game dir]` copies the WHOLE game folder into an Archipelago-owned folder and applies the bsdiff4 patch
shipped inside the apworld (data/devilspire.bsdiff4) to the copy's data.win. The source folder (Steam install) is
only ever read. No Archipelago imports here (except the lazy Utils.user_path fallback) so it can be unit-tested.
"""
from __future__ import annotations

import hashlib
import json
import os
import pkgutil
import re
import shutil
import sys
from pathlib import Path
from typing import Callable, Iterable, Mapping, Optional

STEAM_APP_ID = "1861290"
GAME_FOLDER = "Devil Spire"           # steamapps/common/<this>
EXE_NAME = "Devil Spire.exe"
COPY_DIR_NAME = "DevilSpire"          # <Archipelago user dir>/<this>
PATCH_RESOURCE = "data/devilspire.bsdiff4"
PATCH_INFO_RESOURCE = "data/patch.json"  # {"original_sha256": ..., "patched_sha256": ...}
MARKER_FILE = "ap_patch_info.json"


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
def default_copy_dir() -> Path:
    import Utils  # Archipelago
    return Path(Utils.user_path(COPY_DIR_NAME))


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


# ------------------------------------------------------------------------------------------------ main entry
def auto_patch(game_dir: Optional[Path], dest: Optional[Path] = None, patch: Optional[bytes] = None,
               info: Optional[dict] = None, log: Callable[[str], None] = print) -> Path:
    """Copy game_dir -> dest (atomic: temp dir, then rename) and patch the copy's data.win. Returns dest."""
    if game_dir is None:
        game_dir = find_game_dir()
        if game_dir is None:
            raise PatchError("Devil Spire not found in any Steam library; pass the game folder: /auto_patch <dir>")
    game_dir = Path(game_dir).expanduser().resolve()
    dest = Path(dest if dest is not None else default_copy_dir()).expanduser().resolve()
    if patch is None or info is None:
        patch, info = load_patch()
    src_win = game_dir / "data.win"
    if not src_win.is_file():
        raise PatchError(f"no data.win in {game_dir}")
    if dest == game_dir or game_dir in dest.parents or dest in game_dir.parents:
        raise PatchError(f"destination {dest} must not overlap the game folder {game_dir}")
    got = sha256_file(src_win)
    if got == info["patched_sha256"]:
        raise PatchError(f"{src_win} is already patched; use the original game folder (verify files in Steam)")
    if got != info["original_sha256"]:
        raise PatchError(f"unsupported data.win (sha256 {got}, expected {info['original_sha256']}); "
                         "verify game files in Steam. Other game versions are not supported.")
    log(f"Copying {game_dir} -> {dest}")
    tmp = dest.with_name(dest.name + ".ap-tmp")
    old = dest.with_name(dest.name + ".ap-old")
    for d in (tmp, old):
        if d.exists():
            shutil.rmtree(d)
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(game_dir, tmp, symlinks=False)
        for p in [tmp, *tmp.rglob("*")]:  # read-only sources (or Windows) must not give a read-only copy
            try:
                os.chmod(p, p.stat().st_mode | (0o700 if p.is_dir() else 0o600))
            except OSError:
                pass
        win = tmp / "data.win"
        if sha256_file(win) != info["original_sha256"]:
            raise PatchError("copied data.win does not match the original (disk or copy error)")
        log("Applying patch to the copy's data.win")
        out = apply_bsdiff(win.read_bytes(), patch)
        if hashlib.sha256(out).hexdigest() != info["patched_sha256"]:
            raise PatchError("patched data.win has the wrong checksum; nothing was installed")
        with open(win, "wb") as f:
            f.write(out)
            f.flush()
            os.fsync(f.fileno())
        (tmp / "steam_appid.txt").write_text(STEAM_APP_ID, encoding="ascii")
        (tmp / MARKER_FILE).write_text(json.dumps({"source": str(game_dir), **info}, indent=1), encoding="utf-8")
        if dest.exists():
            os.replace(dest, old)
        os.replace(tmp, dest)
        if old.exists():
            shutil.rmtree(old, ignore_errors=True)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        if old.exists() and not dest.exists():
            os.replace(old, dest)
        raise
    log(f"Done. Patched game: {dest}")
    return dest


def launch_instructions(dest: Path, platform: Optional[str] = None) -> list[str]:
    platform = sys.platform if platform is None else platform
    exe = dest / EXE_NAME
    if platform.startswith("win"):
        return [f"Start the patched game by running: {exe}",
                "(Optional: add it to Steam via Games > Add a Non-Steam Game.)"]
    return ["Add it to Steam: Games > Add a Non-Steam Game > Browse > select",
            f"  {exe}",
            "then right-click it > Properties > Compatibility > force a Proton version. Launch it from Steam.",
            "Your normal Steam install of Devil Spire is unchanged."]
