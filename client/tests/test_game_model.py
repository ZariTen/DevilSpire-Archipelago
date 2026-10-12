"""Item/DeathLink/identity behaviour against the FakeGame model of the GML (no server)."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "worlds-src" / "devilspire"))
import file_protocol as fp  # noqa: E402
from fake_game import FakeGame  # noqa: E402

SLOT = "seed1:0:1"


def setup(d, n_items, slot=SLOT):
    (d / "ap_config.ini").write_text(f"[ap]\ndeath_link=1\nslot_id={slot}\n")
    w = fp.InWriter(d / fp.IN_FILE)
    w.items = [(38470600 + i % 50, f"Item {i}", "Buddy") for i in range(n_items)]
    w.flush()
    return w


class GameModelTests(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.g = FakeGame(self.d)

    def test_bulk_500_items_batches_no_loss_no_dup(self):
        w = setup(self.d, 20)
        self.g.start(); self.g.new_run(); self.g.poll()
        self.assertEqual(self.g.open_chest(), 20)
        w.items += [(38470700, f"burst {i}", "Buddy") for i in range(480)]  # !collect-like burst
        w.flush()
        self.g.poll()
        self.assertEqual(self.g.n, 500)
        opens = []
        while True:
            c = self.g.open_chest()
            if not c:
                break
            opens.append(c)
        self.assertEqual(opens, [100, 100, 100, 100, 80])
        self.assertEqual(self.g.char_items, self.g.items)
        self.assertEqual(len(self.g.char_items), 500)

    def test_new_character_mid_seed_regrants_once(self):
        setup(self.d, 30)
        self.g.start(); self.g.new_run(); self.g.poll()
        self.assertEqual(self.g.open_chest(), 30)
        (self.d / "descent_character.ini").unlink(missing_ok=True)  # player deletes the save / abandons the run
        self.g.new_run()
        self.assertEqual(self.g.open_chest(), 30)
        self.assertEqual(self.g.open_chest(), 0)
        self.assertEqual(self.g.char_items, self.g.items)

    def test_deathlink_ignored_without_active_run(self):
        w = setup(self.d, 1)
        self.g.start(); self.g.poll()                      # title: adopts current seq
        for room, level, granted in (("title", 0, -1), ("charcreation", 0, -1), ("dungeon", 0.5, 0)):
            self.g.goto(room, level)
            self.g.granted = granted
            w.add_death("x"); w.flush(force=True); self.g.poll()
        self.assertEqual(self.g.deaths, [])
        self.g.goto("dungeon", -3)                         # entering the tower later: nothing queued
        self.g.poll()
        self.assertEqual(self.g.deaths, [])
        w._seq += 10
        w.add_death("now"); w.flush(force=True); self.g.poll()
        self.assertEqual(len(self.g.deaths), 1)

    def test_wrong_tag_state_not_trusted(self):
        setup(self.d, 5)
        (self.d / "ap_granted.txt").write_text("5\nother:0:9\n")   # e.g. synced from another PC / seed
        self.g.start()
        self.assertEqual(self.g.granted, -1)
        self.g.poll()
        self.assertEqual(self.g.open_chest(), 0)


class Utf8PathTests(unittest.TestCase):
    def test_accented_paths(self):
        root = Path(tempfile.mkdtemp()) / "Zé Ação Ñ 日本"
        d = root / "AppData" / "Roaming" / "Devil_Spire_AP"
        d.mkdir(parents=True)
        (d / fp.OUT_FILE).write_text("L|38470100|s:0:1\n", encoding="utf-8")
        t = fp.OutTailer(d / fp.OUT_FILE)
        self.assertEqual(t.poll_events()[0].location_id, 38470100)
        w = fp.InWriter(d / fp.IN_FILE)
        w.items = [(1, "Épée ✦", "Zoë")]
        w.flush()
        self.assertIn("Épée ✦|Zoë", (d / fp.IN_FILE).read_text(encoding="utf-8"))
        self.assertTrue(fp.write_config(d, {"base_id": 5}, slot_id="sêed:0:1"))
        self.assertEqual(fp.find_save_dir(env={"APPDATA": str(d.parent)}, home=root, platform="win32"), d)
        fp.store_state(d, {"identity": {"slot_id": "sêed:0:1"}})
        self.assertEqual(fp.load_state(d)["identity"]["slot_id"], "sêed:0:1")
        dest = fp.reset_save_dir(d, "sêed:0:1")
        self.assertTrue((dest / fp.OUT_FILE).exists())


if __name__ == "__main__":
    unittest.main()
