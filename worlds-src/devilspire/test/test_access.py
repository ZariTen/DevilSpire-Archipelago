from test.bases import WorldTestBase

from ..items import ITEM_TABLE, POOL_TEMPLATE, ITEM_NAME_TO_ID, F, T
from ..regions import tier_region_name


class DevilSpireTestBase(WorldTestBase):
    game = "Devil Spire"


class TestTemplate(DevilSpireTestBase):
    def test_template(self) -> None:
        self.assertEqual(len(POOL_TEMPLATE), 110)
        self.assertEqual(len(set(ITEM_NAME_TO_ID.values())), len(ITEM_NAME_TO_ID))
        self.assertFalse([n for n in POOL_TEMPLATE if ITEM_TABLE[n].classification == T])
        self.assertEqual(ITEM_NAME_TO_ID["Orb of Strength"], 38_470_000 + 500 + 100)

    def test_progressive(self) -> None:
        from collections import Counter
        from BaseClasses import ItemClassification as IC
        c = Counter(POOL_TEMPLATE)
        self.assertEqual((c["Progressive Weapon"], c["Progressive Armor"], c["Progressive Shield"],
                          c["Progressive Accessory"], c["Progressive Spellbook"]), (7, 7, 3, 4, 6))
        self.assertEqual(sum(1 for n in POOL_TEMPLATE if ITEM_TABLE[n].classification == IC.progression), 27)
        self.assertEqual(ITEM_NAME_TO_ID["Progressive Weapon"], 38_470_000 + 500 + 160)
        removed = {130, 131, 132} | set(range(140, 151))
        self.assertFalse([n for n, d in ITEM_TABLE.items() if d.code in removed])


class TestFloorChecksDefault(DevilSpireTestBase):
    def test_counts(self) -> None:
        locs = [l for l in self.multiworld.get_locations(1) if l.address is not None]
        self.assertEqual(len(locs), 110)
        self.assertEqual(len(self.multiworld.itempool), 110)

    def test_no_gating(self) -> None:
        """Everything is reachable with an EMPTY inventory; no depth keys exist."""
        self.assertFalse(self.get_items_by_name("Progressive Depth Key"))
        self.assertTrue(self.can_reach_location("Reach Floor -100"))
        self.assertTrue(self.can_reach_location("Gauntlet cleared (Floor -99)"))
        self.assertTrue(self.can_reach_location("Rhamdon defeated"))
        for t in range(10):
            self.assertTrue(self.can_reach_region(tier_region_name(t)))
        self.assertBeatable(True)
        # only the progressive items are progression; they gate nothing (everything reachable with an empty state)
        self.assertFalse([i for i in self.multiworld.itempool if i.advancement and not i.name.startswith("Progressive ")])

    def test_single_golem_check(self) -> None:
        names = [l.name for l in self.multiworld.get_locations(1) if "Golem" in l.name]
        self.assertEqual(len(names), 1)

    def test_floor_99_both(self) -> None:
        self.assertIn("Reach Floor -99", [l.name for l in self.multiworld.get_locations(1)])
        self.assertIn("Gauntlet cleared (Floor -99)", [l.name for l in self.multiworld.get_locations(1)])

    def test_classifications(self) -> None:
        pool = [i.name for i in self.multiworld.itempool]
        self.assertEqual(sorted(pool), sorted(POOL_TEMPLATE))
        self.assertEqual(len(self.get_items_by_name("Orb of Vitality")), 7)


class TestTraps(DevilSpireTestBase):
    options = {"trap_percentage": 100, "floor_checks": "every_floor", "death_link": True}

    def test_traps_replace_filler(self) -> None:
        pool = self.multiworld.itempool
        self.assertEqual(len(pool), 110)
        self.assertEqual(sum(1 for i in pool if i.classification == T),
                         sum(1 for n in POOL_TEMPLATE if ITEM_TABLE[n].classification == F))
        self.assertBeatable(True)


class TestFloorChecks5(DevilSpireTestBase):
    options = {"floor_checks": "every_5th"}

    def test_counts(self) -> None:
        self.assertEqual(len([l for l in self.multiworld.get_locations(1) if l.address]), 30)
        self.assertEqual(len(self.multiworld.itempool), 30)
        names = [l.name for l in self.multiworld.get_locations(1)]
        self.assertIn("Reach Floor -1", names)
        self.assertIn("Reach Floor -6", names)
        self.assertNotIn("Reach Floor -5", names)


class TestFloorChecks10(DevilSpireTestBase):
    options = {"floor_checks": "every_10th"}

    def test_counts(self) -> None:
        self.assertEqual(len([l for l in self.multiworld.get_locations(1) if l.address]), 20)
        self.assertEqual(len(self.multiworld.itempool), 20)
        names = [l.name for l in self.multiworld.get_locations(1)]
        self.assertIn("Reach Floor -11", names)
        self.assertNotIn("Reach Floor -10", names)
        self.assertBeatable(True)


class TestFloorChecksOff(DevilSpireTestBase):
    options = {"floor_checks": "off"}

    def test_counts(self) -> None:
        self.assertEqual(len([l for l in self.multiworld.get_locations(1) if l.address]), 10)
        self.assertEqual(len(self.multiworld.itempool), 10)


class TestSlotData(DevilSpireTestBase):
    """The client needs these keys to write ap_config.ini."""
    options = {"death_link": True, "floor_checks": "every_10th"}

    def test_client_keys(self) -> None:
        sd = self.world.fill_slot_data()
        self.assertEqual(sd["death_link"], 1)
        self.assertEqual(sd["floor_checks"], 2)
        self.assertEqual(sd["base_id"], 38_470_000)
        self.assertNotIn("floor_key_mode", sd)
        self.assertNotIn("starting_depth", sd)
