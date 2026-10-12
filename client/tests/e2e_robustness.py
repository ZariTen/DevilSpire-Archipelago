#!/usr/bin/env python3
"""Robustness e2e WITHOUT the game: real MultiServer(s) + real DevilSpireClient + FakeGame (client/tests/fake_game.py).

Usage: python client/tests/e2e_robustness.py --ap-root /tmp/ap-ds [--python /tmp/ap-venv/bin/python]
Scenarios: game played before the client ever connected (offline checks adopted), client restart with offline
checks, server restart, no item doubling (game restart / client restart / new run), seed switch while the game runs
(backup + stale game + tagged lines of the old seed never sent), same-seed reconnect does not reset.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fake_game import FakeGame  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--ap-root", required=True)
ap.add_argument("--python", default=sys.executable)
ap.add_argument("--port", type=int, default=38992)
a = ap.parse_args()
ROOT, PY = Path(a.ap_root).expanduser(), a.python
CLIENT = Path(__file__).resolve().parent.parent / "DevilSpireClient.py"
tmp = Path(tempfile.mkdtemp(prefix="ds-rob-"))
RUN = tmp / "run.py"
RUN.write_text("import sys, runpy\nsys.path.insert(0, '.')\nimport ModuleUpdate\nModuleUpdate.update_ran = True\n"
               "s = sys.argv[1]; sys.argv = sys.argv[1:]\nrunpy.run_path(s, run_name='__main__')\n")
os.environ["SKIP_REQUIREMENTS_UPDATE"] = "1"
BASE = 38_470_000
procs, results = [], []


def check(name, cond, extra=""):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (f"  {extra}" if extra and not cond else ""), flush=True)


def wait_for(fn, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        v = fn()
        if v:
            return v
        time.sleep(0.3)
    return None


def read(p):
    try:
        return Path(p).read_text()
    except OSError:
        return ""


def generate(tag, names):
    pf = tmp / f"players_{tag}"
    pf.mkdir()
    for n in names:
        (pf / f"{n}.yaml").write_text(f"name: {n}\ngame: Devil Spire\nDevil Spire:\n  floor_checks: every_floor\n")
    out = tmp / f"out_{tag}"
    subprocess.run([PY, str(RUN), "Generate.py", "--player_files_path", str(pf), "--outputpath", str(out),
                    "--spoiler", "0"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   stdin=subprocess.DEVNULL)
    with zipfile.ZipFile(next(out.glob("AP_*.zip"))) as z:
        md = [n for n in z.namelist() if n.endswith(".archipelago")][0]
        z.extract(md, out)
    return out / md


def start_server(md, port, log):
    p = subprocess.Popen([PY, str(RUN), "MultiServer.py", "--port", str(port), str(md)], cwd=ROOT,
                         stdin=subprocess.PIPE, stdout=open(log, "a"), stderr=subprocess.STDOUT)
    procs.append(p)
    time.sleep(3)
    return p


class Client:
    def __init__(self, name, savedir, port, log):
        self.log = log
        self.p = subprocess.Popen([PY, str(CLIENT), "--ap-root", str(ROOT), "--nogui", "--connect",
                                   f"localhost:{port}", "--name", name, "--savedir", str(savedir)],
                                  stdin=subprocess.PIPE, stdout=open(log, "w"), stderr=subprocess.STDOUT, cwd=tmp,
                                  text=True)
        procs.append(self.p)

    def status(self):
        self.p.stdin.write("/apstatus\n")
        self.p.stdin.flush()
        time.sleep(0.6)
        m = re.findall(r"server-checked: (\d+); goal: \w+; slot: (\S+)", read(self.log))
        return (int(m[-1][0]), m[-1][1]) if m else (None, None)

    def checked(self):
        return self.status()[0]

    def kill(self):
        self.p.kill()
        self.p.wait()


try:
    mdA = generate("A", ["Zari", "Buddy"])
    mdB = generate("B", ["Zari"])
    portA, portB = a.port, a.port + 1
    srvA = start_server(mdA, portA, tmp / "serverA.log")
    zd, bd = tmp / "zari", tmp / "buddy"
    bd.mkdir()
    game = FakeGame(zd)

    # 1. played before the client ever connected (the real first-install situation)
    game.start()
    game.new_run()
    game.check(BASE + 100)
    game.check(BASE + 101)
    (zd / "ap_souls_granted.txt").write_text("1\n\n")       # older build parsed "-1" as 1
    (zd / "descent_character.ini").write_text("[Stats]\nFloor=-2\n")
    zc = Client("Zari", zd, portA, tmp / "zari1.log")
    check("offline checks from before the first connection are sent", wait_for(lambda: zc.checked() == 2),
          zc.status())
    sid_a = zc.status()[1]
    check("first connection adopts files (no backup, character kept)",
          not (zd / "ap_backup").exists() and (zd / "descent_character.ini").exists())
    check("souls state repaired to -1", read(zd / "ap_souls_granted.txt") == "-1\n\n")
    game.poll()
    check("running game adopts the slot (ap_granted.txt tagged)", read(zd / "ap_granted.txt") == f"0\n{sid_a}\n",
          read(zd / "ap_granted.txt"))

    # Buddy checks everything -> Zari gets items
    bc = Client("Buddy", bd, portA, tmp / "buddy.log")
    wait_for(lambda: (bd / "ap_config.ini").exists())
    with open(bd / "ap_out.txt", "a") as f:
        f.writelines(f"L|{BASE + i}\n" for i in list(range(10)) + list(range(100, 200)))
    n_items = wait_for(lambda: len([l for l in read(zd / "ap_in.txt").splitlines() if l.startswith("I|")]) > 5
                       and len([l for l in read(zd / "ap_in.txt").splitlines() if l.startswith("I|")]))
    time.sleep(2)
    n_items = len([l for l in read(zd / "ap_in.txt").splitlines() if l.startswith("I|")])
    game.poll()
    got = game.open_chest()
    check("items received and granted once", got == n_items and game.char_items == game.items, (got, n_items))

    # 2. client closed, checks made offline, client restarted
    zc.kill()
    game.check(BASE + 102)
    game.check(BASE + 103)
    zc = Client("Zari", zd, portA, tmp / "zari2.log")
    check("offline checks while the client was closed are sent after restart", wait_for(lambda: zc.checked() == 4),
          zc.status())
    game.poll()
    check("client restart (full ap_in rewrite) grants nothing again", game.open_chest() == 0)

    # 3. server restart while client and game run
    srvA.kill(); srvA.wait()
    time.sleep(1)
    game.check(BASE + 104)
    srvA = start_server(mdA, portA, tmp / "serverA.log")
    check("check made during server downtime is sent after auto-reconnect", wait_for(lambda: zc.checked() == 5, 60),
          zc.status())

    # 4. game restart (Continue) and new run
    game.quit(); game.start(); game.poll()
    check("game restart mid-run: nothing re-granted", game.open_chest() == 0 and game.granted == n_items)
    game.die(); game.new_run(); game.poll()
    check("new run re-grants every item exactly once", game.open_chest() == n_items and game.char_items == game.items)

    # 5. switch to another multiworld while the game is still running
    srvB = start_server(mdB, portB, tmp / "serverB.log")
    zc.kill()
    zc = Client("Zari", zd, portB, tmp / "zari3.log")
    backup = wait_for(lambda: list((zd / "ap_backup").glob("*")) if (zd / "ap_backup").exists() else None)
    check("seed switch: old slot files moved to ap_backup/<time>_<old>",
          backup and (backup[0] / "descent_character.ini").exists() and (backup[0] / "ap_out.txt").exists()
          and not (zd / "descent_character.ini").exists(), backup)
    sid_b = wait_for(lambda: zc.status()[1] if zc.status()[1] not in (None, sid_a) else None)
    check("new slot id differs", sid_b and sid_b != sid_a, (sid_a, sid_b))
    check("server B starts with 0 checks (nothing from seed A sent)", zc.checked() == 0)
    game.poll()
    check("running game turns stale (run inactive)", game.stale and game.granted == -1)
    game.check(BASE + 150)
    with open(zd / "ap_out.txt", "a") as f:   # a line the old session tagged with seed A
        f.write(f"L|{BASE + 151}|{sid_a}\n")
    time.sleep(2)
    check("stale game emits no checks; seed A tagged line is not sent to B", zc.checked() == 0, zc.status())
    game.quit(); game.start(); game.poll()
    check("after restart the old run is inactive (no items from B into A's run)",
          game.granted == -1 and game.open_chest() == 0)
    game.new_run(); game.poll()
    nb = len([l for l in read(zd / "ap_in.txt").splitlines() if l.startswith("I|")])
    check("new run on seed B gets B's items", game.open_chest() == nb)
    game.check(BASE + 100)
    check("seed B checks are sent", wait_for(lambda: zc.checked() == 1), zc.status())

    # 6. same-seed reconnect: no reset
    zc.kill()
    zc = Client("Zari", zd, portB, tmp / "zari4.log")
    wait_for(lambda: zc.checked() == 1)
    check("same-seed reconnect does not create another backup", len(list((zd / "ap_backup").glob("*"))) == 1)

    def own_errors(txt):
        return [l for l in txt.splitlines() if ("ds_client" in l or "file_protocol" in l) and
                ("File " in l or "Error" in l)]
    check("no client tracebacks", not any(own_errors(read(p)) for p in tmp.glob("zari*.log")))
finally:
    for p in procs:
        try:
            p.kill()
        except Exception:
            pass
    print("logs in", tmp)
ok = all(r for _, r in results)
print("RESULT", "ALL PASS" if ok else "FAILURES", f"({sum(r for _, r in results)}/{len(results)})")
sys.exit(0 if ok else 1)
