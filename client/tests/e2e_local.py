#!/usr/bin/env python3
"""End-to-end test WITHOUT the game: local MultiServer + two real DevilSpireClient processes + simulated ap_out.txt.

Usage: python client/tests/e2e_local.py --ap-root ~/.cache/ap-src [--python ~/.cache/ap-venv/bin/python]
Needs an AP checkout whose worlds/devilspire links to worlds-src/devilspire and a venv with AP's requirements.
Generates a 2-player seed (Zari, Buddy; both DeathLink on, floor_checks every_5th), then checks:
config written, location checks, item delivery into the other player's ap_in.txt, DeathLink, goal, reconnect resync.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--ap-root", required=True)
ap.add_argument("--python", default=sys.executable)
ap.add_argument("--port", type=int, default=38991)
a = ap.parse_args()
ROOT = Path(a.ap_root).expanduser()
PY = a.python
HERE = Path(__file__).resolve().parent
CLIENT = HERE.parent / "DevilSpireClient.py"
tmp = Path(tempfile.mkdtemp(prefix="ds-e2e-"))
(tmp / "players").mkdir()
for n in ("Zari", "Buddy"):
    (tmp / "players" / f"{n}.yaml").write_text(
        f"name: {n}\ngame: Devil Spire\nDevil Spire:\n  death_link: true\n  floor_checks: every_5th\n")
RUN = tmp / "run.py"
RUN.write_text("import sys, runpy\nsys.path.insert(0, '.')\nimport ModuleUpdate\nModuleUpdate.update_ran = True\n"
               "s = sys.argv[1]; sys.argv = sys.argv[1:]\nrunpy.run_path(s, run_name='__main__')\n")
os.environ["SKIP_REQUIREMENTS_UPDATE"] = "1"  # venv lacks kivy etc.; headless test
procs = []
results = []


def check(name, cond, extra=""):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (f"  {extra}" if extra and not cond else ""), flush=True)


def wait_for(fn, timeout=20):
    end = time.time() + timeout
    while time.time() < end:
        v = fn()
        if v:
            return v
        time.sleep(0.2)
    return None


def read(p):
    try:
        return Path(p).read_text()
    except OSError:
        return ""


def start_client(name, savedir, log):
    p = subprocess.Popen([PY, str(CLIENT), "--ap-root", str(ROOT), "--nogui", "--connect", f"localhost:{a.port}",
                          "--name", name, "--savedir", str(savedir)],
                         stdin=subprocess.PIPE, stdout=open(log, "w"), stderr=subprocess.STDOUT, cwd=tmp)
    procs.append(p)
    return p


try:
    subprocess.run([PY, str(RUN), "Generate.py", "--player_files_path", str(tmp / "players"),
                    "--outputpath", str(tmp / "out"), "--spoiler", "0"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    zf = next((tmp / "out").glob("AP_*.zip"))
    with zipfile.ZipFile(zf) as z:
        md = [n for n in z.namelist() if n.endswith(".archipelago")][0]
        z.extract(md, tmp / "out")
    server = subprocess.Popen([PY, str(RUN), "MultiServer.py", "--port", str(a.port), "--disable_save",
                               str(tmp / "out" / md)], cwd=ROOT, stdin=subprocess.PIPE,
                              stdout=open(tmp / "server.log", "w"), stderr=subprocess.STDOUT)
    procs.append(server)
    time.sleep(3)
    zd, bd = tmp / "zari_save", tmp / "buddy_save"
    zd.mkdir(); bd.mkdir()
    BASE = 38_470_000
    # stale data from a "previous seed" must be moved away (backup), not sent
    (zd / "ap_out.txt").write_text(f"L|{BASE + 1}\nG|1\n")
    (zd / "ap_client_state.json").write_text(json.dumps({"identity": {"slot_id": "oldseed:0:1"}}))
    zc = start_client("Zari", zd, tmp / "zari.log")
    bc = start_client("Buddy", bd, tmp / "buddy.log")
    cfg = wait_for(lambda: read(zd / "ap_config.ini"))
    check("ap_config.ini written", cfg.startswith(f"[ap]\ndeath_link=1\nfloor_check_step=5\nbase_id={BASE}\n") and "slot_id=" in cfg, repr(cfg))
    check("stale ap_out.txt of another seed moved to ap_backup", wait_for(lambda: read(zd / "ap_out.txt") == "" and
          any((zd / "ap_backup").glob("*/ap_out.txt"))))
    check("ap_in.txt written", wait_for(lambda: (zd / "ap_in.txt").exists()))
    time.sleep(1)
    # simulate the game: boss -9 (id +0), floor 1 (+100), floor 6 (+105), duplicate, garbage, truncated line, partial
    with open(zd / "ap_out.txt", "a") as f:
        f.write(f"S|1|patch started\r\nL|{BASE}\r\nL|{BASE + 100}\r\nL|{BASE + 105}\r\nL|{BASE}\r\nzzz\r\nL|\r\n")
    # each of Zari's locations holds an item for Zari or Buddy; wait until the server processed them
    time.sleep(3)
    ai = wait_for(lambda: read(bd / "ap_in.txt") + read(zd / "ap_in.txt"))
    lines_z = [l for l in read(zd / "ap_in.txt").splitlines() if l.startswith("I|")]
    lines_b = [l for l in read(bd / "ap_in.txt").splitlines() if l.startswith("I|")]
    # Items are placed randomly: 3 checked locations => 3 items spread over both worlds' location pool.
    # Zari receives items located anywhere in the multiworld, so check format / contiguity and total count only.
    check("ap_in lines well-formed (I|idx|id|name|sender), contiguous indexes",
          all(l.split("|")[1] == str(i) and len(l.split("|")) == 5 for i, l in enumerate(lines_z)) and
          all(l.split("|")[1] == str(i) and len(l.split("|")) == 5 for i, l in enumerate(lines_b)))
    # Buddy completes everything he has -> Zari must receive all items placed in Buddy's locations
    bloc = [BASE + i for i in range(10)] + [BASE + 100 + 5 * i for i in range(20)]
    with open(bd / "ap_out.txt", "a") as f:
        for loc in bloc:
            f.write(f"L|{loc}\n")
    zloc = [BASE + i for i in range(10)] + [BASE + 100 + 5 * i for i in range(20)]
    with open(zd / "ap_out.txt", "a") as f:
        for loc in zloc:
            f.write(f"L|{loc}\n")
    n_z = wait_for(lambda: len([l for l in read(zd / "ap_in.txt").splitlines() if l.startswith("I|")]) == 30 and 30)
    n_b = wait_for(lambda: len([l for l in read(bd / "ap_in.txt").splitlines() if l.startswith("I|")]) == 30 and 30)
    check("after all 60 locations checked each slot receives its 30 items", n_z == 30 and n_b == 30,
          f"z={len(read(zd/'ap_in.txt').splitlines())} b={len(read(bd/'ap_in.txt').splitlines())}")
    zi = [l for l in read(zd / "ap_in.txt").splitlines() if l.startswith("I|")]
    check("item names resolved (no numeric fallback)", all(not l.split("|")[3].startswith("Item ") for l in zi), zi[:2])
    check("sender names resolved", {l.split("|")[4] for l in zi} <= {"Zari", "Buddy"})
    # DeathLink: Zari dies -> Buddy's ap_in gets D line, Zari's does not
    with open(zd / "ap_out.txt", "a") as f:
        f.write("D|Died on floor 12\n")
    d = wait_for(lambda: [l for l in read(bd / "ap_in.txt").splitlines() if l.startswith("D|")])
    check("DeathLink Zari->Buddy delivered as D|seq|text", d and d[-1].split("|")[2].startswith("Zari"), d)
    time.sleep(1.5)
    check("no DeathLink echo back to the dying player",
          not [l for l in read(zd / "ap_in.txt").splitlines() if l.startswith("D|")])
    # goal
    with open(zd / "ap_out.txt", "a") as f:
        f.write("G|1\n")
    check("goal sent to server", wait_for(lambda: "Zari" in read(tmp / "server.log") and
                                           "goal" in read(tmp / "server.log").lower()), read(tmp / "server.log")[-400:])
    # truncation of ap_out.txt by the user, then new line still seen (DeathLink Buddy -> Zari)
    (bd / "ap_out.txt").write_text("")
    time.sleep(1)
    with open(bd / "ap_out.txt", "a") as f:
        f.write("D|Died on floor 3\n")
    d2 = wait_for(lambda: [l for l in read(zd / "ap_in.txt").splitlines() if l.startswith("D|")])
    check("after truncating ap_out.txt a new D line is still processed", bool(d2))
    seq_before = int(d2[-1].split("|")[1]) if d2 else 0
    # reconnect: kill Zari's client, restart; full item list is rewritten, old checks not duplicated
    zc.kill(); zc.wait()
    (zd / "ap_in.txt").unlink()
    zc = start_client("Zari", zd, tmp / "zari2.log")
    again = wait_for(lambda: len([l for l in read(zd / "ap_in.txt").splitlines() if l.startswith("I|")]) == 30 and 1)
    check("reconnect rewrites FULL ap_in.txt (30 items)", again)
    time.sleep(2)
    log2 = read(tmp / "zari2.log")
    check("reconnect: same seed not treated as new seed", "belonged to another multiworld" not in log2)
    def own_errors(txt):  # ignore "Could not load world X" noise from unrelated worlds missing optional deps
        return [l for l in txt.splitlines() if ("ds_client" in l or "file_protocol" in l or "DevilSpire" in l)
                and ("File " in l or "Error" in l) and "DevilSpireClient.py\", line" not in l]
    check("no client tracebacks in ds_client/file_protocol",
          not any(own_errors(read(tmp / n)) for n in ("zari.log", "zari2.log", "buddy.log")))
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
