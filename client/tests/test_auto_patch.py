"""Unit tests for auto_patch (needs bsdiff4, an Archipelago requirement): `python -m unittest discover client/tests`.
Optional real-game e2e: set DS_GAME_DIR (read only) and DS_PATCHED_WIN (expected result) to run test_real_game."""
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
ORIG, PATCHED = b"original game data " * 100, b"original GAME data, patched " * 100


def make_game(d: Path, data=ORIG) -> Path:
    d.mkdir(parents=True)
    (d / "data.win").write_bytes(data)
    (d / ap.EXE_NAME).write_bytes(b"MZ")
    (d / "sub").mkdir()
    (d / "sub" / "a.ogg").write_bytes(b"ogg")
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
class AutoPatchTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.root = Path(self.t.name)
        self.patch = bsdiff4.diff(ORIG, PATCHED)
        self.info = {"original_sha256": H(ORIG), "patched_sha256": H(PATCHED)}

    def tearDown(self):
        self.t.cleanup()

    def run_patch(self, game, dest):
        return ap.auto_patch(game, dest, self.patch, self.info, log=lambda s: None)

    def test_copy_and_patch_idempotent(self):
        game = make_game(self.root / "game")
        before = {p: p.read_bytes() for p in game.rglob("*") if p.is_file()}
        dest = self.root / "ap" / "DevilSpire"
        for _ in range(2):
            self.assertEqual(self.run_patch(game, dest), dest.resolve())
            self.assertEqual((dest / "data.win").read_bytes(), PATCHED)
            self.assertEqual((dest / "steam_appid.txt").read_text(), "1861290")
            self.assertEqual((dest / "sub/a.ogg").read_bytes(), b"ogg")
            self.assertEqual(sorted(p.name for p in (self.root / "ap").iterdir()), ["DevilSpire"])
        self.assertEqual({p: p.read_bytes() for p in game.rglob("*") if p.is_file()}, before)  # source untouched

    def test_rejects_wrong_or_patched_source(self):
        for data in (b"other version", PATCHED):
            game = make_game(self.root / H(data)[:6], data)
            with self.assertRaises(ap.PatchError):
                self.run_patch(game, self.root / "dest")
            self.assertFalse((self.root / "dest").exists())

    def test_bad_patch_keeps_previous_copy(self):
        game = make_game(self.root / "game")
        dest = self.root / "dest"
        self.run_patch(game, dest)
        self.info["patched_sha256"] = "0" * 64
        with self.assertRaises(ap.PatchError):
            self.run_patch(game, dest)
        self.assertEqual((dest / "data.win").read_bytes(), PATCHED)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["dest", "game"])

    def test_refuses_overlap(self):
        game = make_game(self.root / "game")
        with self.assertRaises(ap.PatchError):
            self.run_patch(game, game / "DevilSpire")

    @unittest.skipUnless(os.environ.get("DS_GAME_DIR") and os.environ.get("DS_PATCHED_WIN"), "real game not given")
    def test_real_game(self):
        patch, info = ap.load_patch()
        dest = ap.auto_patch(Path(os.environ["DS_GAME_DIR"]), self.root / "DevilSpire", patch, info, log=print)
        self.assertEqual(ap.sha256_file(dest / "data.win"), ap.sha256_file(Path(os.environ["DS_PATCHED_WIN"])))
        self.assertTrue((dest / ap.EXE_NAME).is_file())


if __name__ == "__main__":
    unittest.main()
