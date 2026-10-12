"""Devil Spire <-> client file protocol (pure Python, NO Archipelago imports so it can be unit-tested anywhere).

See patch/README.md for the protocol definition. Fan-made, unofficial.
"""
from __future__ import annotations

import glob
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

OUT_FILE = "ap_out.txt"
IN_FILE = "ap_in.txt"
CONFIG_FILE = "ap_config.ini"
STATE_FILE = "ap_client_state.json"  # client-private: remembers which seed/slot the save dir last belonged to

ENV_SAVE_DIR = "DEVILSPIRE_SAVE_DIR"
SAVE_DIR_NAME = "Devil_Spire"
FLOOR_STEP_BY_OPTION = {0: 1, 1: 5, 2: 10, 3: 0}  # slot_data floor_checks -> ap_config floor_check_step


# ---------------------------------------------------------------------------------------------- save dir discovery
def candidate_save_dirs(env: Optional[Mapping[str, str]] = None, home: Optional[Path] = None,
                        platform: Optional[str] = None) -> list[Path]:
    """All plausible save dirs, most specific first (env var, Windows %APPDATA%, Proton prefixes)."""
    env = os.environ if env is None else env
    home = Path.home() if home is None else home
    platform = sys.platform if platform is None else platform
    out: list[Path] = []
    if env.get(ENV_SAVE_DIR):
        out.append(Path(env[ENV_SAVE_DIR]).expanduser())
    if env.get("APPDATA"):
        out.append(Path(env["APPDATA"]) / SAVE_DIR_NAME)
    if platform.startswith("win"):
        out.append(home / "AppData" / "Roaming" / SAVE_DIR_NAME)
    steam_roots = [home / ".local/share/Steam", home / ".steam/steam", home / ".steam/root",
                   home / ".var/app/com.valvesoftware.Steam/.local/share/Steam"]
    seen = set()
    for root in steam_roots:
        pattern = str(root / "steamapps/compatdata/*/pfx/drive_c/users/*/AppData/Roaming" / SAVE_DIR_NAME)
        for m in sorted(glob.glob(pattern)):
            real = os.path.realpath(m)
            if real not in seen:
                seen.add(real)
                out.append(Path(m))
    return out


def find_save_dir(explicit: Optional[str] = None, env: Optional[Mapping[str, str]] = None,
                  home: Optional[Path] = None, platform: Optional[str] = None) -> Optional[Path]:
    """explicit path (CLI arg) wins, then the env var, then auto-detection. Returns None if nothing exists.
    If several auto-detected dirs exist, the one with the most recently modified ap_/save file wins."""
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.is_dir() else None
    cands = [c for c in candidate_save_dirs(env, home, platform) if c.is_dir()]
    if not cands:
        return None
    env = os.environ if env is None else env
    if env.get(ENV_SAVE_DIR) and cands[0] == Path(env[ENV_SAVE_DIR]).expanduser():
        return cands[0]

    def newest(d: Path) -> float:
        try:
            return max([f.stat().st_mtime for f in d.iterdir() if f.is_file()] or [d.stat().st_mtime])
        except OSError:
            return 0.0
    return max(cands, key=newest)


# ---------------------------------------------------------------------------------------------- atomic writes
def atomic_write_text(path: Path, text: str) -> None:
    """Write tmp file in the same dir, fsync, then os.replace (atomic on POSIX and Windows)."""
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass
    os.replace(tmp, path)


# ---------------------------------------------------------------------------------------------- ap_config.ini
def floor_step(floor_checks: int) -> int:
    return FLOOR_STEP_BY_OPTION.get(int(floor_checks), 1)


def render_config(slot_data: Mapping, poll_frames: Optional[int] = None) -> str:
    lines = ["[ap]",
             f"death_link={1 if slot_data.get('death_link') else 0}",
             f"floor_check_step={floor_step(slot_data.get('floor_checks', 0))}",
             f"base_id={int(slot_data['base_id'])}"]
    if poll_frames:
        lines.append(f"poll_frames={int(poll_frames)}")
    return "\n".join(lines) + "\n"


def write_config(save_dir: Path, slot_data: Mapping, poll_frames: Optional[int] = None) -> bool:
    """Returns True if the file content changed."""
    p = Path(save_dir) / CONFIG_FILE
    text = render_config(slot_data, poll_frames)
    try:
        if p.read_text(encoding="utf-8") == text:
            return False
    except OSError:
        pass
    atomic_write_text(p, text)
    return True


# ---------------------------------------------------------------------------------------------- ap_out.txt parsing
@dataclass(frozen=True)
class OutEvent:
    kind: str                     # "L" location, "G" goal, "D" death, or other informational kinds
    location_id: Optional[int] = None
    text: str = ""


def parse_out_line(line: str) -> Optional[OutEvent]:
    """Parse one ap_out.txt line. Returns None for blank/garbage lines (incl. truncated numbers)."""
    line = line.strip().lstrip("\ufeff\x00")
    if len(line) < 2 or line[1] != "|":
        return None
    kind, rest = line[0], line[2:]
    if kind == "L":
        field_ = rest.split("|", 1)[0].strip()
        if field_.isdigit():
            return OutEvent("L", location_id=int(field_))
        return None
    if kind == "G":
        return OutEvent("G", text=rest) if rest.split("|", 1)[0].strip() == "1" else None
    if kind == "D":
        return OutEvent("D", text=rest)
    if kind in "XNSE":
        return OutEvent(kind, text=rest)
    return None


class OutTailer:
    """Reads new complete lines of ap_out.txt by byte offset.

    * the game appends; only lines terminated by '\\n' are consumed (a half-written last line waits)
    * if the file shrinks/disappears (client or user truncated it) the offset resets to 0
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.offset = 0

    def reset(self) -> None:
        self.offset = 0

    def truncate_file(self) -> None:
        try:
            open(self.path, "wb").close()
        except OSError:
            pass
        self.offset = 0

    def poll(self) -> list[str]:
        try:
            size = self.path.stat().st_size
        except OSError:
            self.offset = 0
            return []
        if size < self.offset:
            self.offset = 0
        if size == self.offset:
            return []
        try:
            with open(self.path, "rb") as f:
                f.seek(self.offset)
                data = f.read(size - self.offset)
        except OSError:
            return []
        end = data.rfind(b"\n")
        if end < 0:
            return []
        self.offset += end + 1
        return [ln.decode("utf-8", "replace") for ln in data[:end].split(b"\n")]

    def poll_events(self) -> list[OutEvent]:
        return [e for e in map(parse_out_line, self.poll()) if e is not None]


# ---------------------------------------------------------------------------------------------- ap_in.txt rendering
def clean_field(s: object) -> str:
    return str(s).replace("|", "/").replace("\r", " ").replace("\n", " ").strip()


@dataclass
class InWriter:
    """Holds the state that ap_in.txt is rendered from (FULL list each time) and writes it atomically."""
    path: Path
    items: list[tuple[int, str, str]] = field(default_factory=list)   # (item id, name, sender) in AP order
    deaths: list[tuple[int, str]] = field(default_factory=list)       # (seq, text)
    max_deaths: int = 5
    _last: Optional[str] = None
    _seq: int = 0

    def next_seq(self) -> int:
        """Strictly increasing and survives client restarts (time based)."""
        self._seq = max(self._seq + 1, int(time.time()))
        return self._seq

    def add_death(self, text: str) -> int:
        seq = self.next_seq()
        self.deaths.append((seq, text))
        del self.deaths[:-self.max_deaths]
        return seq

    def render(self) -> str:
        out = [f"I|{i}|{item_id}|{clean_field(name)}|{clean_field(sender)}"
               for i, (item_id, name, sender) in enumerate(self.items)]
        out += [f"D|{seq}|{clean_field(text)}" for seq, text in self.deaths]
        return "\n".join(out) + ("\n" if out else "")

    def flush(self, force: bool = False) -> bool:
        text = self.render()
        if not force and text == self._last:
            return False
        atomic_write_text(self.path, text)
        self._last = text
        return True


# ---------------------------------------------------------------------------------------------- session identity
def load_state(save_dir: Path) -> dict:
    import json
    try:
        return json.loads((Path(save_dir) / STATE_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def store_state(save_dir: Path, state: dict) -> None:
    import json
    atomic_write_text(Path(save_dir) / STATE_FILE, json.dumps(state))
