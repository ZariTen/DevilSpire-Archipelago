"""Python model of the patched game's file side (mirrors patch/gml: ap_init, ap_read_config, ap_slot_check, ap_poll,
ap_emit, ap_new_run, ap_grant_pending, ap_drop_spawn, ap_drop_taken, ap_save_granted, ap_death_send). Used by the e2e tests.

Items: weightless ones are applied when processed; weighted ones (ap_item_weighted.gml) go to `drops` and lie on the
ground (at most 60 at once) until picked up. Run state and the character are only written together (commit = save_game +
ap_save_granted: floor change, camp grant, new run, death); quit + Continue restores the last commit."""
from collections import Counter
from pathlib import Path

BASE = 38470000
GROUND_CAP = 60


def weighted(item_id):
    rel = item_id - BASE - 500
    return 120 <= rel <= 122 or 140 <= rel <= 151


def _digits(s):
    return "".join(c for c in s if c.isdigit())


class FakeGame:
    def __init__(self, save_dir: Path):
        self.d = Path(save_dir)
        self.running = False
        self.char_items: list[int] = []   # items applied to the live character
        self.saved_char: list[int] = []   # character as last saved (Continue restores it)
        self.drops: list[int] = []        # received-item indexes of weighted items still waiting on the ground
        self.ground: list[int] = []       # indexes lying in the current room

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
        """commit (ap_save_granted): run state + character together"""
        if self.granted < 0:
            self.drops = []
        self.c_granted, self.c_drops = self.granted, list(self.drops)
        self.saved_char = list(self.char_items)
        self.write_granted()

    def write_granted(self):
        (self.d / "ap_granted.txt").write_text(
            f"{self.c_granted}\n{self.slot_id}\n{','.join(map(str, self.c_drops))}\n")

    # --- lifecycle
    def start(self):
        self.d.mkdir(parents=True, exist_ok=True)
        self.running, self.stale, self.n, self.items = True, False, 0, []
        cfg = self._config()
        self.slot_id = cfg
        self.granted, gslot, self.drops, self.ground = -1, "", [], []
        self.char_items = list(self.saved_char)
        g = self._read("ap_granted.txt")
        if g is not None:
            lines = g.splitlines() + ["", "", ""]
            if _digits(lines[0]):
                self.granted = -1 if lines[0].startswith("-") else int(_digits(lines[0]))
            gslot = lines[1]
            for t in lines[2].split(","):
                if _digits(t) and int(_digits(t)) not in self.drops:
                    self.drops.append(int(_digits(t)))
        if cfg and gslot and gslot != cfg:
            self.granted = -1
        if self.granted < 0:
            self.drops = []
        self.c_granted, self.c_drops = self.granted, list(self.drops)
        self.write_granted()
        self.dl_init, self.dl_seq, self.room, self.level, self.alive, self.deaths = False, 0, "title", 0, True, []
        self.emit("S|4|patch started")

    def quit(self):
        self.running = False

    def poll(self):
        if not self.running:
            return
        cfg = self._config()
        if cfg and cfg != self.slot_id and not self.stale:
            if self.slot_id == "":
                self.slot_id = cfg
                self.write_granted()   # committed state only
            else:
                self.stale, self.granted = True, -1
                self.save_granted()
        if self.stale:
            return
        txt = self._read("ap_in.txt") or ""
        maxd = 0
        for line in txt.split("\n"):
            if line.startswith("I|") and line.count("|") >= 4:
                f = line.split("|")
                if _digits(f[1]) and _digits(f[2]) and int(f[1]) == self.n:
                    self.items.append(int(f[2]))
                    self.n += 1
            elif line.startswith("D|"):
                f = line.split("|")
                if _digits(f[1]):
                    maxd = max(maxd, int(_digits(f[1])))
        if not self.dl_init:
            self.dl_init, self.dl_seq = True, maxd
        elif maxd > self.dl_seq:
            self.dl_seq = maxd
            in_run = self.room == "dungeon" and self.level < 0 and self.granted >= 0 and self.alive
            if in_run:
                self.alive = False
                self.deaths.append(maxd)
                self.die()
            else:
                self.emit("X|deathlink ignored (no active run)")

    def new_run(self):
        self.granted, self.char_items, self.drops, self.ground = 0, [], [], []
        self.save_granted()
        self.emit("N|1|new descent run")

    def grant_tick(self):
        """one ap_poll item step (player alive in the dungeon): process up to 100 items, commit at the camp,
        spawn missing ground items. Returns the number of items processed."""
        if self.stale or self.granted < 0 or self.room != "dungeon" or not self.alive:
            return 0
        cnt = 0
        while self.granted < self.n and cnt < 100:   # batch limit as in ap_grant_pending.gml
            item = self.items[self.granted]
            if weighted(item):
                if self.granted not in self.drops:
                    self.drops.append(self.granted)
            else:
                self.char_items.append(item)
            self.granted += 1
            cnt += 1
        if cnt and self.level == 0.5:
            self.save_granted()
        self.spawn()
        return cnt

    def spawn(self):
        self.ground = [i for i in self.ground if i in self.drops]
        for i in self.drops:
            if len(self.ground) >= GROUND_CAP:
                break
            if i not in self.ground and i < self.n:
                self.ground.append(i)

    def pick_up(self, idx):
        if idx not in self.ground:
            return False
        self.ground.remove(idx)
        self.drops.remove(idx)
        self.char_items.append(self.items[idx])
        return True

    def collect_all(self):
        """at the camp: let the game process everything, pick up every ground item, then enter the tower.
        Returns the number of items processed."""
        self.goto("dungeon", 0.5)
        total = 0
        while True:
            c = self.grant_tick()
            for i in list(self.ground):
                self.pick_up(i)
            self.spawn()
            if not c and not self.ground:
                break
            total += c
        self.next_floor(-1)
        return total

    def next_floor(self, level):
        if self.level == 0.5 and self.granted >= 0:
            self.drops = []   # ap_leave_room: untaken camp ground items are forfeited for this run
        self.room, self.level, self.ground = "dungeon", level, []
        self.save_granted()

    def owned(self):
        return Counter(self.char_items)

    def check(self, loc):
        self.emit(f"L|{loc}")

    def goto(self, room, level):
        if (room, level) != (self.room, self.level):
            self.ground = []   # leaving a room removes its instances (no Destroy event)
        self.room, self.level = room, level

    def die(self):
        self.granted, self.drops, self.ground = -1, [], []
        self.save_granted()
