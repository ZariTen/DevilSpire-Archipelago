import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "worlds-src" / "devilspire"))
import health  # noqa: E402


class HealthTests(unittest.TestCase):
    def test_datawin_cached_and_messages(self):
        d = Path(tempfile.mkdtemp())
        (d / "data.win").write_bytes(b"x")
        calls = []
        states = iter(["original", "patched"])
        chk = health.DataWinCheck(lambda p: calls.append(p) or SimpleNamespace(state=next(states)))
        self.assertIn("NOT patched", chk.check(d))
        self.assertIn("/auto_patch", chk.check(d))
        self.assertEqual(len(calls), 1)               # unchanged file: no re-hash
        (d / "data.win").write_bytes(b"yy")
        self.assertIsNone(chk.check(d))
        self.assertEqual(len(calls), 2)
        self.assertIsNone(chk.check(None))

    def test_protocol(self):
        self.assertIsNone(health.protocol_warning(4, 4))
        self.assertIsNone(health.protocol_warning(None, 4))
        self.assertIn("/auto_patch", health.protocol_warning(1, 4))
        a, b = "Archipelago v0.1.0 (aaaaaaa)", "Archipelago v0.1.0 (bbbbbbb)"
        self.assertIsNone(health.protocol_warning(4, 4, a, a))
        self.assertIsNone(health.protocol_warning(4, 4, None, a))  # older build without label: data.win check covers it
        self.assertIn(a, health.protocol_warning(4, 4, a, b))

    def test_unpatched_activity_and_cloud(self):
        roam = Path(tempfile.mkdtemp())
        ap, orig = roam / "Devil_Spire_AP", roam / "Devil_Spire"
        ap.mkdir(); orig.mkdir()
        (orig / "descent_character.ini").write_text("old")
        w = health.OriginalSaveWatch()
        self.assertIsNone(w.check(ap))
        t = time.time() + 5
        (orig / "descent_character.ini").write_text("new")
        os.utime(orig / "descent_character.ini", (t, t))
        self.assertIn("UNPATCHED", w.check(ap))
        self.assertIsNone(health.cloud_warning(ap))
        (ap / "steam_autocloud.vdf").write_text("")
        self.assertIn("Steam Cloud", health.cloud_warning(ap))

    def test_monitor_reports_changes_only(self):
        out = []
        m = health.HealthMonitor(out.append)
        for msg in ("a", "a", None, "a"):
            m.report("k", msg)
        self.assertEqual(out, ["a", "a"])


if __name__ == "__main__":
    unittest.main()
