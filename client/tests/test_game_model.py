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
import fake_game as fg  # noqa: E402
from fake_game import FakeGame  # noqa: E402
from collections import Counter  # noqa: E402

SLOT = "seed1:0:1"
CODES = (100, 101, 102, 103, 104, 110, 111, 112, 113, 120, 121, 122, 151, 160, 161, 162, 163, 164)


def setup(d, n_items, slot=SLOT):
    (d / "ap_config.ini").write_text(f"[ap]\ndeath_link=1\nslot_id={slot}\n")
    w = fp.InWriter(d / fp.IN_FILE)
    w.items = [(38470500 + CODES[i % len(CODES)], f"Item {i}", "Buddy") for i in range(n_items)]
    w.flush()
    return w


class GameModelTests(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.g = FakeGame(self.d)

    def test_bulk_500_items_batches_no_loss_no_dup(self):
        w = setup(self.d, 20)
        self.g.start(); self.g.new_run(); self.g.poll()
        self.assertEqual(self.g.collect_all(), 20)
        w.items += [(38470500 + CODES[(i * 7) % len(CODES)], f"burst {i}", "Buddy") for i in range(480)]  # !collect-like burst
        w.flush()
        self.g.poll()
        self.assertEqual(self.g.n, 500)
        self.g.goto("dungeon", 0.5)
        ticks = []
        while True:
            c = self.g.grant_tick()
            if not c:
                break
            ticks.append(c)
            self.assertLessEqual(len(self.g.ground), fg.GROUND_CAP)
        self.assertEqual(ticks, [100, 100, 100, 100, 80])
        self.g.collect_all()
        self.assertEqual(len(self.g.owned() - self.g.expected()), 4)   # same run also keeps the gear tiers it had before
        self.g.die(); self.g.new_run(); self.g.collect_all()         # a fresh run: everything once, best gear tier only
        self.assertEqual(self.g.owned(), self.g.expected())

    def test_classification(self):
        for code in (100, 101, 102, 103, 104, 110, 111, 112, 113, 164, 200, 201, 202):
            self.assertFalse(fg.weighted(38470500 + code), code)
        for code in (120, 121, 122, 151, 160, 161, 162, 163):
            self.assertTrue(fg.weighted(38470500 + code), code)

    def test_camp_weightless_direct_weighted_on_ground(self):
        setup(self.d, 0)
        w = fp.InWriter(self.d / fp.IN_FILE)
        w.items = [(38470600, "STR", "B"), (38470660, "Sword", "B"), (38470610, "Gold", "B"), (38470620, "Pack", "B")]
        w.flush()
        self.g.start(); self.g.new_run(); self.g.poll(); self.g.goto("dungeon", 0.5)
        self.assertEqual(self.g.grant_tick(), 4)
        self.assertEqual(self.g.char_items, [38470600, 38470610])
        self.assertEqual(sorted(self.g.ground), [10, 30])
        # quit at the camp before picking up, Continue: ground items come back, weightless not doubled
        self.g.quit(); self.g.start(); self.g.poll(); self.g.goto("dungeon", 0.5)
        self.assertEqual(self.g.grant_tick(), 0)
        self.assertEqual(sorted(self.g.ground), [10, 30])
        self.g.pick_up(10)
        # quit after picking up but before any save: rolled back together (sword back on the ground, not in inventory)
        self.g.quit(); self.g.start(); self.g.poll(); self.g.goto("dungeon", 0.5); self.g.grant_tick()
        self.assertEqual(sorted(self.g.ground), [10, 30])
        self.assertNotIn(38470660, self.g.char_items)
        self.g.pick_up(10); self.g.next_floor(-1)            # entering the tower saves
        self.g.quit(); self.g.start(); self.g.poll(); self.g.goto("dungeon", -1); self.g.grant_tick()
        self.assertEqual(self.g.ground, [])                 # untaken camp pack forfeited for this run; sword kept once
        self.assertEqual(self.g.owned()[38470660], 1)
        self.assertNotIn(38470620, self.g.char_items)
        self.g.die(); self.g.new_run(); self.g.goto("dungeon", 0.5); self.g.grant_tick()
        self.assertEqual(sorted(self.g.ground), [10, 30])     # next run: re-granted as usual

    def test_progressive_best_tier_only(self):
        setup(self.d, 0)
        w = fp.InWriter(self.d / fp.IN_FILE)
        W, A, S = 38470660, 38470661, 38470664
        w.items = [(W, "PW", "B"), (S, "PS", "B"), (W, "PW", "B"), (A, "PA", "B"), (W, "PW", "B"), (S, "PS", "B")]
        w.flush()
        self.g.start(); self.g.new_run(); self.g.poll(); self.g.goto("dungeon", 0.5)
        self.assertEqual(self.g.grant_tick(), 6)
        self.assertEqual(sorted(self.g.ground), [30, 31, 32, 33, 40])   # weapon tier 3 only (idx 4), armor tier 1 set
        self.assertEqual(self.g.copies(4), 3)
        self.assertEqual(self.g.char_items, [S, S])                    # every spellbook copy is granted
        self.g.collect_all()
        self.assertEqual(self.g.owned(), self.g.expected())
        w.items.append((W, "PW", "B")); w.flush(); self.g.poll(); self.g.goto("dungeon", -3)
        self.g.grant_tick()
        self.assertEqual(self.g.ground, [60])                          # mid-run copy 4: the new tier at the player
        self.assertEqual(self.g.copies(6), 4)
        self.g.die(); self.g.new_run(); self.g.goto("dungeon", 0.5); self.g.grant_tick()
        self.assertEqual(sorted(self.g.ground), [30, 31, 32, 33, 60])  # next run: only the best weapon

    def test_mid_run_upgrade_then_continue(self):
        """e2e flake case: a newer progressive copy arrives at the camp after a run started; then quit + Continue.
        Old tier stays, new tier is added, nothing is granted twice and nothing is lost."""
        setup(self.d, 0)
        w = fp.InWriter(self.d / fp.IN_FILE)
        W, M = 38470660, 38470600
        w.items = [(W, "PW", "B"), (M, "x", "B")]
        w.flush()
        self.g.start(); self.g.new_run(); self.g.poll(); self.g.collect_all()
        w.items.append((W, "PW", "B")); w.flush(); self.g.poll()
        self.g.collect_all()
        self.assertEqual(self.g.owned(), Counter({W: 2, M: 1}))        # tier 1 kept + tier 2 added
        self.assertEqual(self.g.granted, 3)
        self.g.quit(); self.g.start(); self.g.poll(); self.g.collect_all()
        self.assertEqual(self.g.owned(), Counter({W: 2, M: 1}))        # Continue: nothing re-granted
        self.g.die(); self.g.new_run(); self.g.collect_all()
        self.assertEqual(self.g.owned(), self.g.expected())            # next run: best tier only

    def test_mid_run_items(self):
        w = setup(self.d, 2)
        self.g.start(); self.g.new_run(); self.g.poll(); self.g.collect_all()
        self.g.goto("dungeon", -5)
        w.items += [(38470601, "INT", "B"), (38470661, "Armor", "B")]
        w.flush(); self.g.poll()
        self.assertEqual(self.g.grant_tick(), 2)
        self.assertIn(38470601, self.g.char_items)           # weightless: applied at once
        self.assertEqual(self.g.ground, [30, 31, 32, 33])     # weighted: full armor set dropped at the player
        self.g.quit(); self.g.start(); self.g.poll(); self.g.goto("dungeon", -5)
        self.assertEqual(self.g.grant_tick(), 2)             # not saved yet: re-processed once after Continue
        self.assertEqual(self.g.owned()[38470601], 2)        # setup item 1 is also INT
        self.g.next_floor(-6); self.g.grant_tick()
        self.assertEqual(self.g.ground, [30, 31, 32, 33])     # left behind: spawned again on the next floor
        [self.g.pick_up(k) for k in (30, 31, 32, 33)]; self.g.next_floor(-7)
        self.assertEqual(self.g.owned(), self.g.expected())

    def test_new_character_mid_seed_regrants_once(self):
        setup(self.d, 30)
        self.g.start(); self.g.new_run(); self.g.poll()
        self.assertEqual(self.g.collect_all(), 30)
        (self.d / "descent_character.ini").unlink(missing_ok=True)  # player deletes the save / abandons the run
        self.g.new_run()
        self.assertEqual(self.g.collect_all(), 30)
        self.assertEqual(self.g.collect_all(), 0)
        self.assertEqual(self.g.owned(), self.g.expected())

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
        self.assertEqual(self.g.collect_all(), 0)


class HeartbeatTests(unittest.TestCase):
    def test_no_grants_until_client_alive(self):
        d = Path(tempfile.mkdtemp())
        setup(d, 3)
        (d / "ap_heartbeat.txt").write_text("1|old:0:1|Zari\n")      # left behind by a closed client
        g = FakeGame(d, require_heartbeat=True)
        g.start(); g.new_run(); g.poll(); g.goto("dungeon", 0.5)
        self.assertEqual(g.grant_tick(), 0)
        g.check(38470100)                                             # checks still recorded offline
        (d / "ap_heartbeat.txt").write_text("2|seed1:0:1|Zari\n")    # client connected
        g.poll()
        self.assertEqual(g.grant_tick(), 3)


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.g = FakeGame(self.d)
        setup(self.d, 0)

    def out(self):
        return [l.split("|")[1] for l in (self.d / "ap_out.txt").read_text().splitlines() if l.startswith("L|")]

    def test_locked_chest_per_floor_once(self):
        self.g.start(); self.g.new_run(); self.g.poll(); self.g.goto("dungeon", -3)
        self.assertTrue(self.g.take_locked_ap())
        self.assertFalse(self.g.take_locked_ap())               # once per floor
        for n in (9, 10, 99, 100):                              # boss, shop, gauntlet, goal floors: none
            self.g.goto("dungeon", -n)
            self.assertFalse(self.g.locked_ap_chest())
        self.g.goto("dungeon", 0.5)
        self.assertFalse(self.g.locked_ap_chest())              # camp: none
        self.g.die(); self.g.new_run(); self.g.goto("dungeon", -3)
        self.assertFalse(self.g.locked_ap_chest())              # sent: a normal locked chest in later runs
        self.g.quit(); self.g.start(); self.g.poll(); self.g.goto("dungeon", -98)
        self.assertTrue(self.g.take_locked_ap())                # flags survive restarts
        self.assertEqual(self.out(), ["38470303", "38470398"])

    def test_shop_slots_fixed_and_once(self):
        self.g.start(); self.g.new_run(); self.g.poll()
        self.g.goto("dungeon", -9)
        self.assertEqual(self.g.shop_stands(), [])
        self.g.goto("dungeon", -20)
        self.assertEqual(self.g.shop_stands(), [2, 3])
        self.assertTrue(self.g.buy_ap(3))
        self.g.die(); self.g.new_run(); self.g.goto("dungeon", -20)
        self.assertEqual(self.g.shop_stands(), [2])            # a stand only shows while its check is unsent
        self.g.goto("dungeon", -100)
        self.assertEqual(self.g.shop_stands(), [])
        self.assertEqual(self.out(), ["38470253"])

    def test_slot_switch_and_old_format_reset(self):
        (self.d / "ap_checks.txt").write_text("1" * 99 + "\n" + "1" * 18 + "\nother:0:9\n")
        self.g.start(); self.g.goto("dungeon", -2)
        self.assertTrue(self.g.locked_ap_chest())               # other slot's file is not trusted
        self.g.goto("dungeon", -10)
        self.assertEqual(self.g.shop_stands(), [0, 1])
        (self.d / "ap_checks.txt").write_text("3,0,0,0,0,0,0,0,0,0\n" + "0" * 18 + f"\n{SLOT}\n")
        self.g.quit(); self.g.start(); self.g.goto("dungeon", -1)
        self.assertTrue(self.g.locked_ap_chest())               # old per-band line: reset, no crash


class SlotSwitchTests(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        setup(self.d, 3)
        self.g = FakeGame(self.d)

    def switch(self, slot):
        (self.d / "ap_config.ini").write_text(f"[ap]\nslot_id={slot}\n")
        self.g.poll()

    def test_title_switch_adopts_live(self):
        self.g.start(); self.g.poll()
        self.switch("seed2:0:1")
        self.assertFalse(self.g.stale)
        self.assertEqual(self.g.slot_id, "seed2:0:1")
        self.g.new_run(); self.g.poll()
        self.assertEqual(self.g.collect_all(), 3)
        self.g.check(38470101)
        self.assertTrue((self.d / "ap_out.txt").read_text().rstrip().endswith("|seed2:0:1"))

    def test_tower_switch_stale_until_run_left(self):
        self.g.start(); self.g.new_run(); self.g.poll(); self.g.collect_all(); self.g.goto("dungeon", -4)
        self.switch("seed2:0:1")
        self.assertTrue(self.g.stale)
        self.assertEqual(self.g.granted, -1)
        self.g.check(38470101)
        self.assertNotIn("38470101", (self.d / "ap_out.txt").read_text())   # nothing from A's run goes to B
        self.g.die(); self.g.goto("title", 0); self.g.poll()
        self.assertFalse(self.g.stale)
        self.assertEqual(self.g.slot_id, "seed2:0:1")
        self.assertEqual(self.g.collect_all(), 0)                           # old run stays inactive

    def test_new_game_right_after_death_adopts_first(self):
        self.g.start(); self.g.new_run(); self.g.poll(); self.g.goto("dungeon", -4)
        self.switch("seed2:0:1")
        self.g.die(); self.g.goto("charcreation", 0)
        self.g.new_run()                                                    # before any poll
        self.assertFalse(self.g.stale)
        self.assertEqual(self.g.granted, 0)
        self.g.poll()
        self.assertEqual(self.g.collect_all(), 3)


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
