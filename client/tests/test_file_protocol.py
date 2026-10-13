"""Unit tests for the file protocol logic. No Archipelago, no server: `python -m unittest discover client/tests`."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "worlds-src" / "devilspire"))
import file_protocol as fp  # noqa: E402


class ParseTests(unittest.TestCase):
    def test_lines(self):
        self.assertEqual(fp.parse_out_line("L|38470100"), fp.OutEvent("L", location_id=38470100))
        self.assertEqual(fp.parse_out_line("L|38470100|seed:0:1\r"), fp.OutEvent("L", location_id=38470100, slot="seed:0:1"))
        self.assertEqual(fp.parse_out_line("L|38470100|\r"), fp.OutEvent("L", location_id=38470100))  # empty tag
        self.assertEqual(fp.parse_out_line("G|1|s:0:2").slot, "s:0:2")
        self.assertEqual(fp.parse_out_line("G|1").kind, "G")
        self.assertEqual(fp.parse_out_line("D|Died on floor 12").text, "Died on floor 12")
        self.assertEqual(fp.parse_out_line("X|death caused by DeathLink").kind, "X")
        self.assertEqual(fp.parse_out_line("S|1|patch started").kind, "S")
        self.assertEqual(fp.parse_out_line("S|3|Archipelago v0.1.0 (6d49c01)").text, "3|Archipelago v0.1.0 (6d49c01)")

    def test_garbage(self):
        for bad in ["", "   ", "L|", "L|abc", "L38470100", "G|0", "Z|1", "L|-5", "\x00\x00", "|"]:
            self.assertIsNone(fp.parse_out_line(bad), bad)


class TailTests(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.p = self.d / "ap_out.txt"
        self.t = fp.OutTailer(self.p)

    def test_missing_and_empty(self):
        self.assertEqual(self.t.poll(), [])
        self.p.write_bytes(b"")
        self.assertEqual(self.t.poll(), [])

    def test_incremental_and_partial_line(self):
        self.p.write_bytes(b"S|1|x\r\nL|10\r\nL|1")  # last line half written
        self.assertEqual([e.kind for e in self.t.poll_events()], ["S", "L"])
        with open(self.p, "ab") as f:
            f.write(b"1\r\nG|1\r\n")
        evs = self.t.poll_events()
        self.assertEqual([(e.kind, e.location_id) for e in evs], [("L", 11), ("G", None)])
        self.assertEqual(self.t.poll_events(), [])

    def test_replaced_file_resets_offset(self):
        d = Path(tempfile.mkdtemp())
        p = d / "ap_out.txt"
        p.write_text("L|1\nL|2\n")
        t = fp.OutTailer(p)
        self.assertEqual(len(t.poll()), 2)
        tmp = d / "new"
        tmp.write_text("L|3\nL|4\nL|5\n")  # rotated: a different, longer file
        os.replace(tmp, p)
        self.assertEqual(t.poll(), ["L|3", "L|4", "L|5"])

    def test_truncation_resets_offset(self):
        self.p.write_bytes(b"L|1\nL|2\nL|3\n")
        self.assertEqual(len(self.t.poll_events()), 3)
        self.p.write_bytes(b"L|9\n")  # shorter than offset -> truncated + rewritten
        self.assertEqual([e.location_id for e in self.t.poll_events()], [9])
        self.p.write_bytes(b"")
        self.assertEqual(self.t.poll_events(), [])
        self.p.write_bytes(b"L|4\n")
        self.assertEqual([e.location_id for e in self.t.poll_events()], [4])

    def test_deleted_file(self):
        self.p.write_bytes(b"L|1\n")
        self.t.poll()
        self.p.unlink()
        self.assertEqual(self.t.poll(), [])
        self.p.write_bytes(b"L|2\n")
        self.assertEqual([e.location_id for e in self.t.poll_events()], [2])

    def test_truncate_file_helper(self):
        self.p.write_bytes(b"L|1\n")
        self.t.poll()
        self.t.truncate_file()
        self.assertEqual(self.p.read_bytes(), b"")
        self.assertEqual(self.t.offset, 0)

    def test_garbage_and_invalid_utf8(self):
        self.p.write_bytes(b"\xff\xfe junk\nL|5\n\n\nL|x\n")
        self.assertEqual([e.location_id for e in self.t.poll_events()], [5])


class InWriterTests(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.w = fp.InWriter(self.d / "ap_in.txt")

    def test_full_list_in_order(self):
        self.w.items = [(38470600, "Orb of Vitality", "Alice"), (38470601, "Yellow Orb (Gold)", "Bob|x")]
        self.assertTrue(self.w.flush())
        self.assertEqual((self.d / "ap_in.txt").read_text(),
                         "I|0|38470600|Orb of Vitality|Alice\nI|1|38470601|Yellow Orb (Gold)|Bob/x\n")
        self.assertFalse(self.w.flush())  # unchanged -> no rewrite
        self.w.items.append((1, "Name\nwith newline", "C"))
        self.assertTrue(self.w.flush())
        self.assertEqual(len((self.d / "ap_in.txt").read_text().splitlines()), 3)

    def test_deaths_increasing(self):
        s1 = self.w.add_death("a")
        s2 = self.w.add_death("b")
        self.assertGreater(s2, s1)
        self.w.flush()
        lines = (self.d / "ap_in.txt").read_text().splitlines()
        self.assertEqual(lines, [f"D|{s1}|a", f"D|{s2}|b"])
        for i in range(10):
            self.w.add_death(str(i))
        self.assertEqual(len(self.w.deaths), 5)

    def test_atomic_no_tmp_left(self):
        self.w.items = [(1, "x", "y")]
        self.w.flush()
        self.assertEqual(sorted(os.listdir(self.d)), ["ap_in.txt"])

    def test_empty(self):
        self.assertTrue(self.w.flush(force=True))
        self.assertEqual((self.d / "ap_in.txt").read_text(), "")


class ConfigTests(unittest.TestCase):
    def test_mapping(self):
        for opt, step in [(0, 1), (1, 5), (2, 10), (3, 0), (4, 2)]:
            t = fp.render_config({"death_link": 1, "floor_checks": opt, "base_id": 38470000})
            self.assertIn(f"floor_check_step={step}", t)
        t = fp.render_config({"death_link": 0, "floor_checks": 0, "base_id": 38470000})
        self.assertEqual(t, "[ap]\ndeath_link=0\nfloor_check_step=1\nbase_id=38470000\n")
        self.assertIn("floor_check_step=2", fp.render_config({"floor_checks": 4, "chest_checks": 3, "base_id": 1}))

    def test_write_config_idempotent(self):
        d = Path(tempfile.mkdtemp())
        sd = {"death_link": True, "floor_checks": 2, "base_id": 5}
        self.assertTrue(fp.write_config(d, sd))
        self.assertFalse(fp.write_config(d, sd))
        self.assertIn("floor_check_step=10", (d / "ap_config.ini").read_text())


class IdentityTests(unittest.TestCase):
    def test_reset_moves_slot_files_only(self):
        d = Path(tempfile.mkdtemp())
        for n in ("descent_character.ini", "corpse.ini", "ap_granted.txt", "ap_out.txt", "ap_client_state.json",
                  "souls.ini", "unlocks.ini"):
            (d / n).write_text(n)
        dest = fp.reset_save_dir(d, "old:0:1")
        self.assertEqual(dest.parent, d / fp.BACKUP_DIR)
        self.assertTrue(dest.name.endswith("old_0_1"))
        self.assertEqual(sorted(p.name for p in d.iterdir()), ["ap_backup", "souls.ini", "unlocks.ini"])
        self.assertEqual((dest / "descent_character.ini").read_text(), "descent_character.ini")
        self.assertIsNone(fp.reset_save_dir(d, "x"))  # nothing left to move
        (d / "ap_out.txt").write_text("again")
        dest2 = fp.reset_save_dir(d, "old:0:1")  # same second: must not collide
        self.assertNotEqual(dest, dest2)

    def test_repair_souls(self):
        d = Path(tempfile.mkdtemp())
        self.assertFalse(fp.repair_souls_file(d))
        (d / "ap_souls_granted.txt").write_text("1\n\n")
        self.assertTrue(fp.repair_souls_file(d))
        self.assertEqual((d / "ap_souls_granted.txt").read_text(), "-1\n\n")
        (d / "ap_souls_granted.txt").write_text("3\nseed:0:1\n")  # tagged: real state, keep
        self.assertFalse(fp.repair_souls_file(d))

    def test_stable_item_order(self):
        a, b, c, s = (1, 10, 2), (2, 11, 2), (3, 12, 3), (4, -2, 1)
        o = fp.stable_item_order([], [a, b, s, s])
        self.assertEqual(o, [list(a), list(b), list(s), list(s)])
        # server lost b (crash before autosave), then it comes back after c: indexes of a, b, s stay
        o = fp.stable_item_order(o, [a, s, s, c])
        o = fp.stable_item_order(o, [a, s, s, c, b])
        self.assertEqual(o, [list(a), list(b), list(s), list(s), list(c)])
        self.assertEqual(fp.stable_item_order(o, [s, s, s]), o + [list(s)])  # third starting item

    def test_slot_id(self):
        self.assertEqual(fp.make_slot_id("123", 0, 2), "123:0:2")
        self.assertEqual(fp.make_slot_id("a|b", 0, 1), "a/b:0:1")


class SaveDirTests(unittest.TestCase):
    def test_proton_autodetect_and_priority(self):
        home = Path(tempfile.mkdtemp())
        a = home / ".local/share/Steam/steamapps/compatdata/111/pfx/drive_c/users/steamuser/AppData/Roaming/Devil_Spire_AP"
        b = home / ".local/share/Steam/steamapps/compatdata/222/pfx/drive_c/users/steamuser/AppData/Roaming/Devil_Spire_AP"
        a.mkdir(parents=True)
        b.mkdir(parents=True)
        (a / "x").write_text("1")
        os.utime(a / "x", (1, 1))
        (b / "ap_out.txt").write_text("2")
        self.assertEqual(fp.find_save_dir(env={}, home=home, platform="linux"), b)  # newest wins
        override = home / "custom"
        override.mkdir()
        self.assertEqual(fp.find_save_dir(env={"DEVILSPIRE_SAVE_DIR": str(override)}, home=home, platform="linux"), override)
        self.assertEqual(fp.find_save_dir(str(a), env={"DEVILSPIRE_SAVE_DIR": str(override)}, home=home), a)
        self.assertIsNone(fp.find_save_dir(str(home / "nope"), env={}, home=home))

    def test_other_library_and_original_ignored(self):
        home = Path(tempfile.mkdtemp())
        lib = home / "lib"
        sa = home / ".local/share/Steam/steamapps"
        sa.mkdir(parents=True)
        (sa / "libraryfolders.vdf").write_text(f'"libraryfolders" {{ "1" {{ "path" "{lib}" }} }}')
        roam = lib / "steamapps/compatdata/1861290/pfx/drive_c/users/steamuser/AppData/Roaming"
        (roam / "Devil_Spire").mkdir(parents=True)  # original game's saves: never used
        self.assertIsNone(fp.find_save_dir(env={}, home=home, platform="linux"))
        (roam / "Devil_Spire_AP").mkdir()
        self.assertEqual(fp.find_save_dir(env={}, home=home, platform="linux"), roam / "Devil_Spire_AP")

    def test_none_and_windows(self):
        home = Path(tempfile.mkdtemp())
        self.assertIsNone(fp.find_save_dir(env={}, home=home, platform="linux"))
        appdata = home / "AppData" / "Roaming"
        (appdata / "Devil_Spire_AP").mkdir(parents=True)
        self.assertEqual(fp.find_save_dir(env={"APPDATA": str(appdata)}, home=home, platform="win32"),
                         appdata / "Devil_Spire_AP")



class ScoutTests(unittest.TestCase):
    def test_sanitize(self):
        self.assertEqual(fp.scout_text("A|B#C\nD"), "A/B C D")
        self.assertEqual(fp.scout_text("José ☃"), "Jos? ?")
        self.assertEqual(len(fp.scout_text("x" * 100)), 40)
        self.assertEqual([fp.scout_tag(f) for f in (0, 1, 2, 4, 5)], ["filler", "progression", "useful", "trap", "trap"])

    def test_write(self):
        d = Path(tempfile.mkdtemp())
        fp.write_scouts(d, "s:0:1", [(301, "Progressive Weapon", "you", 1), (250, "Sword#2", "Al|ex", 0)])
        self.assertEqual((d / fp.SCOUTS_FILE).read_text(),
                         "s:0:1\n250|Sword 2|Al/ex|filler\n301|Progressive Weapon|you|progression\n")
        self.assertIn(fp.SCOUTS_FILE, fp.RESET_FILES)

if __name__ == "__main__":
    unittest.main()
