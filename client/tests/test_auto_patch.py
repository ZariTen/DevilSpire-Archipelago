"""Unit tests for the in-place patcher (needs bsdiff4, an Archipelago requirement):
`python -m unittest discover client/tests`.
Optional real-game e2e: DS_GAME_DIR = a WRITABLE TEMP COPY of the game folder, DS_PATCHED_WIN = expected result."""
import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "worlds-src" / "devilspire"))
import auto_patch as ap  # noqa: E402

try:
    import bsdiff4
except ImportError:
    bsdiff4 = None

H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
ORIG, OLD, PATCHED = b"original game data " * 100, b"old AP build " * 100, b"original GAME data, patched " * 100
QUIET = dict(log=lambda s: None)


def make_game(d: Path, data=ORIG) -> Path:
    d.mkdir(parents=True)
    (d / "data.win").write_bytes(data)
    (d / "Devil Spire.exe").write_bytes(b"MZ")
    return d


class VdfTests(unittest.TestCase):
    def test_parse(self):
        new = '"libraryfolders"\n{\n "0"\n {\n  "path"\t\t"/home/u/.local/share/Steam"\n  "label" ""\n }\n' \
              ' "1"\n {\n  "path"\t\t"/mnt/NVME/SteamLibrary"\n  "apps" { "1861290" "86000000" }\n }\n}'
        self.assertEqual(ap.parse_libraryfolders(new),
                         [Path("/home/u/.local/share/Steam"), Path("/mnt/NVME/SteamLibrary")])
        old = '"LibraryFolders"\n{\n "TimeNextStatsReport" "123"\n "1" "D:\\\\SteamLibrary"\n}'
        self.assertEqual(ap.parse_libraryfolders(old), [Path("D:\\SteamLibrary")])

    def test_find_game_dir(self):
        with tempfile.TemporaryDirectory() as t:
            home = Path(t)
            lib = home / "lib"
            make_game(lib / "steamapps/common" / ap.GAME_FOLDER)
            sa = home / ".local/share/Steam/steamapps"
            sa.mkdir(parents=True)
            (sa / "libraryfolders.vdf").write_text(f'"libraryfolders" {{ "1" {{ "path" "{lib}" }} }}')
            self.assertEqual(ap.find_game_dir(env={}, home=home, platform="linux"),
                             lib / "steamapps/common" / ap.GAME_FOLDER)
            self.assertIsNone(ap.find_game_dir(env={}, home=home / "nothing", platform="linux"))


@unittest.skipIf(bsdiff4 is None, "bsdiff4 not installed")
class InPlaceTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.game = make_game(Path(self.t.name) / "game")
        self.patch = bsdiff4.diff(ORIG, PATCHED)
        self.info = {"original_sha256": H(ORIG), "patched_sha256": H(PATCHED),
                     "known_patched_sha256": [H(OLD), H(PATCHED)]}

    def tearDown(self):
        self.t.cleanup()

    def patch_(self, **kw):
        return ap.auto_patch(self.game, self.patch, self.info, **kw, **QUIET)

    def files(self):
        return sorted(p.name for p in self.game.iterdir())

    def test_patch_restore_cycle(self):
        self.assertEqual(self.patch_().state, "patched")
        self.assertEqual((self.game / "data.win").read_bytes(), PATCHED)
        self.assertEqual((self.game / ap.BACKUP).read_bytes(), ORIG)
        self.assertEqual(self.files(), ["Devil Spire.exe", "ap_patch_info.json", "data.win", "data.win.orig"])
        self.assertEqual(self.patch_().state, "patched")  # second run: no-op
        self.assertEqual(self.patch_(force=True).state, "patched")  # re-patch from backup
        self.assertEqual((self.game / ap.BACKUP).read_bytes(), ORIG)
        st = ap.restore(self.game, self.info, **QUIET)
        self.assertEqual((st.state, st.backup), ("original", "missing"))
        self.assertEqual((self.game / "data.win").read_bytes(), ORIG)
        self.assertEqual(self.files(), ["Devil Spire.exe", "data.win"])

    def test_upgrade_from_older_build(self):
        self.patch_()
        (self.game / "data.win").write_bytes(OLD)
        self.assertEqual(ap.patch_status(self.game, self.info).state, "outdated")
        self.assertEqual(self.patch_().state, "patched")

    def test_unknown_and_missing_backup(self):
        (self.game / "data.win").write_bytes(b"other version")
        with self.assertRaisesRegex(ap.PatchError, "Verify integrity"):
            self.patch_()
        self.assertEqual((self.game / "data.win").read_bytes(), b"other version")
        self.assertEqual(self.files(), ["Devil Spire.exe", "data.win"])
        (self.game / "data.win").write_bytes(PATCHED)  # patched but no backup
        with self.assertRaisesRegex(ap.PatchError, "missing.*Verify integrity"):
            ap.restore(self.game, self.info, **QUIET)
        with self.assertRaisesRegex(ap.PatchError, "missing"):
            self.patch_(force=True)
        (self.game / ap.BACKUP).write_bytes(b"corrupt")
        with self.assertRaisesRegex(ap.PatchError, "invalid"):
            ap.restore(self.game, self.info, **QUIET)
        self.assertEqual((self.game / ap.BACKUP).read_bytes(), b"corrupt")

    def test_restore_refuses_after_game_update(self):
        self.patch_()
        (self.game / "data.win").write_bytes(b"new game version from steam")
        with self.assertRaisesRegex(ap.PatchError, "game update"):
            ap.restore(self.game, self.info, **QUIET)
        self.assertEqual((self.game / "data.win").read_bytes(), b"new game version from steam")
        with self.assertRaisesRegex(ap.PatchError, "updated apworld"):
            self.patch_()

    def test_accented_game_dir(self):
        game = make_game(Path(self.t.name) / "Jogos Ção" / "Devil Spire")
        self.assertEqual(ap.auto_patch(game, self.patch, self.info, **QUIET).state, "patched")
        self.assertEqual(ap.restore(game, self.info, **QUIET).state, "original")

    def test_never_overwrites_bad_backup(self):
        (self.game / ap.BACKUP).write_bytes(b"someone's file")
        self.patch_()
        self.assertEqual((self.game / (ap.BACKUP + ".invalid")).read_bytes(), b"someone's file")
        self.assertEqual((self.game / ap.BACKUP).read_bytes(), ORIG)

    def test_bad_result_leaves_original(self):
        self.info["patched_sha256"] = "0" * 64
        with self.assertRaises(ap.PatchError):
            self.patch_()
        self.assertEqual((self.game / "data.win").read_bytes(), ORIG)
        self.assertNotIn(ap.TMP, self.files())

    @unittest.skipUnless(os.environ.get("DS_GAME_DIR") and os.environ.get("DS_PATCHED_WIN"), "real game not given")
    def test_real_game(self):
        game = Path(os.environ["DS_GAME_DIR"])
        orig_sha = ap.sha256_file(game / "data.win")
        patch, info = ap.load_patch()
        self.assertEqual(orig_sha, info["original_sha256"])
        self.assertEqual(ap.auto_patch(game, patch, info, log=print).state, "patched")
        self.assertEqual(ap.sha256_file(game / "data.win"), ap.sha256_file(Path(os.environ["DS_PATCHED_WIN"])))
        self.assertEqual(ap.auto_patch(game, patch, info, log=print).state, "patched")  # idempotent
        self.assertEqual(ap.sha256_file(game / "data.win"), info["patched_sha256"])
        ap.restore(game, info, log=print)
        self.assertEqual(ap.sha256_file(game / "data.win"), orig_sha)
        self.assertFalse((game / ap.BACKUP).exists())
        with self.assertRaisesRegex(ap.PatchError, "backup data.win.orig is missing"):
            (game / "data.win").write_bytes(Path(os.environ["DS_PATCHED_WIN"]).read_bytes())
            ap.restore(game, info, log=print)


if __name__ == "__main__":
    unittest.main()
