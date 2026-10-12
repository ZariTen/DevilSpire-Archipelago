"""Python model of the patched game's file side (mirrors patch/gml: ap_init, ap_read_config, ap_slot_check, ap_poll,
ap_emit, ap_new_run, ap_grant_pending, ap_chest_open, ap_save_granted, ap_death_send). Used by the e2e tests."""
from pathlib import Path


def _digits(s):
    return "".join(c for c in s if c.isdigit())


class FakeGame:
    def __init__(self, save_dir: Path):
        self.d = Path(save_dir)
        self.running = False
        self.char_items: list[int] = []   # items applied to the current character (what the save would hold)

    # --- files
    def _read(self, n):
        try:
            return (self.d / n).read_text()
        except OSError:
            return None

    def _config(self):
        txt = self._read("ap_config.ini")
        if txt is None:
            return ""
        kv = dict(l.split("=", 1) for l in txt.splitlines() if "=" in l)
        return kv.get("slot_id", "")

    def emit(self, line):
        k = line[0]
        if self.stale and k in "LGD":
            return
        if k in "LG":
            line += "|" + self.slot_id
        with open(self.d / "ap_out.txt", "a", newline="") as f:
            f.write(line + "\r\n")   # GMS on Windows writes CRLF

    def save_granted(self):
        (self.d / "ap_granted.txt").write_text(f"{self.granted}\n{self.slot_id}\n")

    # --- lifecycle
    def start(self):
        self.d.mkdir(parents=True, exist_ok=True)
        self.running, self.stale, self.n, self.items = True, False, 0, []
        cfg = self._config()
        self.slot_id = cfg
        self.granted, gslot = -1, ""
        g = self._read("ap_granted.txt")
        if g is not None:
            lines = g.splitlines() + ["", ""]
            if _digits(lines[0]):
                self.granted = -1 if lines[0].startswith("-") else int(_digits(lines[0]))
            gslot = lines[1]
        if cfg and gslot and gslot != cfg:
            self.granted = -1
        self.save_granted()
        self.emit("S|1|patch started")

    def quit(self):
        self.running = False

    def poll(self):
        if not self.running:
            return
        cfg = self._config()
        if cfg and cfg != self.slot_id and not self.stale:
            if self.slot_id == "":
                self.slot_id = cfg
                self.save_granted()
            else:
                self.stale, self.granted = True, -1
                self.save_granted()
        if self.stale:
            return
        txt = self._read("ap_in.txt") or ""
        for line in txt.split("\n"):
            if line.startswith("I|") and line.count("|") >= 4:
                f = line.split("|")
                if _digits(f[1]) and _digits(f[2]) and int(f[1]) == self.n:
                    self.items.append(int(f[2]))
                    self.n += 1

    def new_run(self):
        self.granted, self.char_items = 0, []
        self.save_granted()
        self.emit("N|1|new descent run")

    def open_chest(self):
        if self.stale or self.granted < 0:
            return 0
        cnt = 0
        while self.granted < self.n:
            self.char_items.append(self.items[self.granted])
            self.granted += 1
            cnt += 1
        if cnt:
            self.save_granted()
        return cnt

    def check(self, loc):
        self.emit(f"L|{loc}")

    def die(self):
        self.granted = -1
        self.save_granted()
