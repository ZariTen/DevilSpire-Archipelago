"""Devil Spire <-> client file protocol (pure Python, NO Archipelago imports so it can be unit-tested anywhere).

See docs/dev/patch.md for the protocol definition. Fan-made, unofficial.
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
SAVE_DIR_NAME = "Devil_Spire_AP"  # patched game's own save folder (GEN8 Name, set by ApPatch.csx)
FLOOR_STEP_BY_OPTION = {0: 1, 1: 5, 2: 10, 3: 0, 4: 2}  # slot_data floor_checks -> ap_config floor_check_step


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
    try:
        from .auto_patch import steam_libraries
    except ImportError:
        from auto_patch import steam_libraries  # type: ignore
    seen = set()
    for root in steam_libraries(env, home, platform):  # all libraries: Proton prefixes live in the game's library
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
    # Windows: os.replace fails with PermissionError while the game has the target open; retry briefly, then give up
    # (callers keep the content dirty and retry on the next poll)
    for attempt in range(5):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.05)


# ---------------------------------------------------------------------------------------------- ap_config.ini
def floor_step(floor_checks: int) -> int:
    return FLOOR_STEP_BY_OPTION.get(int(floor_checks), 1)


HEARTBEAT_FILE = "ap_heartbeat.txt"
SCOUTS_FILE = "ap_scouts.txt"
MSGS_FILE = "ap_msgs.txt"


def append_msg(save_dir: Path, idx: int, text: str, keep: int = 20) -> None:
    """ap_msgs.txt: "idx|text" popups for the game (idx increasing), only the last `keep` lines are kept"""
    p = Path(save_dir) / MSGS_FILE
    try:
        old = p.read_text(encoding="utf-8").splitlines()
    except OSError:
        old = []
    lines = (old + [f"{int(idx)}|{scout_text(text, 60)}"])[-keep:]
    atomic_write_text(p, "\n".join(lines) + "\n")
SCOUT_OFFSETS = tuple(range(250, 268)) + tuple(300 + n for n in range(1, 99) if n % 10 not in (0, 9))  # shops, locked chests


def scout_text(s: object, limit: int = 40) -> str:
    """game-safe text: one line, no field separator, no '#' (GMS1 newline), printable ASCII only, short"""
    t = "".join(c if 32 <= ord(c) < 127 else "?" for c in clean_field(s).replace("#", " "))
    return t[:limit].strip()


def scout_tag(flags: int) -> str:
    return "trap" if flags & 4 else "progression" if flags & 1 else "useful" if flags & 2 else "filler"


def write_scouts(save_dir: Path, slot_id: str, rows: Iterable[tuple[int, str, str, int]]) -> None:
    """ap_scouts.txt for the Archipelago Item description: line 1 = slot id, then "offset|item|player|tag"
    (offset = location id - base_id; player "you" for the own slot)."""
    lines = [clean_field(slot_id)] + [f"{int(o)}|{scout_text(i)}|{scout_text(p, 24)}|{scout_tag(int(f))}"
                                      for o, i, p, f in sorted(rows)]
    atomic_write_text(Path(save_dir) / SCOUTS_FILE, "\n".join(lines) + "\n")


def write_heartbeat(save_dir: Path, counter: int, slot_id: str, name: str) -> None:
    """Liveness for the game (title "Client not connected" warning; no item grants before it): rewritten every few
    seconds while connected with the server's item list. The game treats it as stale ~10 s after the last change."""
    atomic_write_text(Path(save_dir) / HEARTBEAT_FILE, f"{int(counter)}|{clean_field(slot_id)}|{clean_field(name)}\n")


def render_config(slot_data: Mapping, poll_frames: Optional[int] = None, slot_id: Optional[str] = None) -> str:
    lines = ["[ap]",
             f"death_link={1 if slot_data.get('death_link') else 0}",
             f"floor_check_step={floor_step(slot_data.get('floor_checks', 0))}",
             f"difficulty={int(slot_data.get('difficulty', 3))}",
             f"base_id={int(slot_data['base_id'])}"]
    if poll_frames:
        lines.append(f"poll_frames={int(poll_frames)}")
    if slot_id:
        # lets the game reset its "souls granted once" state when the multiworld seed / slot changes
        lines.append(f"slot_id={clean_field(slot_id)}")
    return "\n".join(lines) + "\n"


def write_config(save_dir: Path, slot_data: Mapping, poll_frames: Optional[int] = None,
                 slot_id: Optional[str] = None) -> bool:
    """Returns True if the file content changed."""
    p = Path(save_dir) / CONFIG_FILE
    text = render_config(slot_data, poll_frames, slot_id)
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
    slot: Optional[str] = None    # L/G: slot id the game belonged to when it emitted the line (None = untagged)


def parse_out_line(line: str) -> Optional[OutEvent]:
    """Parse one ap_out.txt line. Returns None for blank/garbage lines (incl. truncated numbers)."""
    line = line.strip().lstrip("\ufeff\x00")
    if len(line) < 2 or line[1] != "|":
        return None
    kind, rest = line[0], line[2:]
    parts = rest.split("|")
    tag = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
    if kind == "L":
        field_ = parts[0].strip()
        if field_.isdigit():
            return OutEvent("L", location_id=int(field_), slot=tag)
        return None
    if kind == "G":
        return OutEvent("G", text=rest, slot=tag) if parts[0].strip() == "1" else None
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
        self.file_id: Optional[tuple] = None   # (st_dev, st_ino) of the file the offset belongs to

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
            st = self.path.stat()
        except OSError:
            self.offset = 0
            return []
        size, fid = st.st_size, (st.st_dev, st.st_ino)
        if size < self.offset or (self.file_id is not None and fid != self.file_id and st.st_ino):
            self.offset = 0   # truncated, or replaced by another file (rotation)
        self.file_id = fid
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
# Files that belong to one multiworld slot. On a seed/slot switch they are MOVED (never deleted) into
# ap_backup/<timestamp>_<old slot>/ so the next run starts clean. Meta progression (souls.ini, unlocks.ini) stays.
RESET_FILES = ("descent_character.ini", "corpse.ini", "ap_granted.txt", "ap_souls_granted.txt", "ap_checks.txt", OUT_FILE, IN_FILE,
               CONFIG_FILE, STATE_FILE, SCOUTS_FILE, MSGS_FILE)
BACKUP_DIR = "ap_backup"


def make_slot_id(seed_name: object, team: object, slot: object) -> str:
    return clean_field(f"{seed_name}:{team}:{slot}")


def reset_save_dir(save_dir: Path, label: str = "") -> Optional[Path]:
    """Move this slot's files into a timestamped backup folder. Returns that folder (None if nothing to move)."""
    save_dir = Path(save_dir)
    present = [n for n in RESET_FILES if (save_dir / n).exists()]
    if not present:
        return None
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in label)[:60]
    base = save_dir / BACKUP_DIR / (time.strftime("%Y%m%d-%H%M%S") + (f"_{safe}" if safe else ""))
    dest, n = base, 1
    while dest.exists():
        n += 1
        dest = base.with_name(f"{base.name}_{n}")
    dest.mkdir(parents=True)
    for name in present:
        os.replace(save_dir / name, dest / name)
    return dest


def repair_souls_file(save_dir: Path) -> bool:
    """Older patch builds parsed "-1" in ap_souls_granted.txt as 1 (souls of item 0/1 then never granted). Before the
    first connection no item can have been received, so an untagged file is reset to "-1". Returns True if changed."""
    p = Path(save_dir) / "ap_souls_granted.txt"
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return False
    if (len(lines) < 2 or not lines[1].strip()) and lines and lines[0].strip() != "-1":
        atomic_write_text(p, "-1\n\n")
        return True
    return False

def load_state(save_dir: Path) -> dict:
    import json
    try:
        return json.loads((Path(save_dir) / STATE_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def stable_item_order(known: Sequence[Sequence[int]], received: Iterable[Sequence[int]]) -> list[list[int]]:
    """Keep ap_in.txt indexes stable: the game stores items BY INDEX and remembers how many it granted, so an index
    must never change meaning. `known` = previous order of (item, location, player) keys, `received` = the server's
    current list. Known keys keep their index (also if the server temporarily lost them, e.g. after a crash before
    its autosave: they were already granted), new keys are appended in server order. Multiset-aware."""
    from collections import Counter
    order = [list(k) for k in known]
    have = Counter(tuple(k) for k in order)
    for k in received:
        t = tuple(int(x) for x in k)
        if have[t] > 0:
            have[t] -= 1
        else:
            order.append(list(t))
    return order


def store_state(save_dir: Path, state: dict) -> None:
    import json
    atomic_write_text(Path(save_dir) / STATE_FILE, json.dumps(state))
