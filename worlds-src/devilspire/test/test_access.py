from test.bases import WorldTestBase

from ..regions import tier_region_name


class DevilSpireTestBase(WorldTestBase):
    game = "Devil Spire"


class TestProgressive(DevilSpireTestBase):
    options = {"floor_key_mode": "progressive"}

    def test_gating(self) -> None:
        self.assertEqual(len(self.get_items_by_name("Progressive Depth Key")), 9)
        self.assertFalse(self.can_reach_location("Abomination defeated (Floor -19)"))
        self.assertTrue(self.can_reach_location("Slime defeated (Floor -9)"))
        self.collect(self.get_item_by_name("Progressive Depth Key"))
        self.assertTrue(self.can_reach_location("Abomination defeated (Floor -19)"))
        self.assertFalse(self.can_reach_location("Idol defeated (Floor -29)"))
        self.assertBeatable(False)

    def test_beatable(self) -> None:
        self.collect_all_but([])
        self.assertBeatable(True)


class TestIndividual(DevilSpireTestBase):
    options = {"floor_key_mode": "individual"}

    def test_dependency(self) -> None:
        from ..items import key_name
        tier9 = ["Gauntlet cleared (Floor -99)", "Rhamdon defeated"] + [f"Reach Floor -{n}" for n in range(91, 101)]
        self.assertAccessDependency(tier9, [[key_name(9)]], only_check_listed=True)
        self.assertTrue(self.can_reach_region(tier_region_name(0)))


class TestOff(DevilSpireTestBase):
    options = {"floor_key_mode": "off"}

    def test_open(self) -> None:
        self.assertTrue(self.can_reach_location("Robot defeated (Floor -89)"))
        self.assertBeatable(True)


class TestStartDepthAndExtras(DevilSpireTestBase):
    options = {"starting_depth": 9, "trap_percentage": 100, "floor_checks": "every_floor", "death_link": True}

    def test_open(self) -> None:
        self.assertBeatable(True)
        self.assertEqual(len(self.multiworld.get_locations(1)), 10 + 100 + 1)


class TestFloorChecksDefault(DevilSpireTestBase):
    def test_counts(self) -> None:
        locs = [l for l in self.multiworld.get_locations(1) if l.address is not None]
        self.assertEqual(len(locs), 110)
        self.assertEqual(len(self.multiworld.itempool), 110)
        self.assertEqual(len(self.get_items_by_name("Progressive Depth Key")), 9)

    def test_floor_access(self) -> None:
        self.assertTrue(self.can_reach_location("Reach Floor -1"))
        self.assertTrue(self.can_reach_location("Reach Floor -10"))
        self.assertFalse(self.can_reach_location("Reach Floor -11"))
        self.assertFalse(self.can_reach_location("Reach Floor -100"))
        self.collect(self.get_items_by_name("Progressive Depth Key")[:1])
        self.assertTrue(self.can_reach_location("Reach Floor -20"))
        self.assertFalse(self.can_reach_location("Reach Floor -21"))
        self.collect(self.get_items_by_name("Progressive Depth Key")[1:])
        self.assertTrue(self.can_reach_location("Reach Floor -100"))

    def test_single_golem_check(self) -> None:
        names = [l.name for l in self.multiworld.get_locations(1) if "Golem" in l.name]
        self.assertEqual(len(names), 1)

    def test_floor_99_both(self) -> None:
        self.assertIn("Reach Floor -99", [l.name for l in self.multiworld.get_locations(1)])
        self.assertIn("Gauntlet cleared (Floor -99)", [l.name for l in self.multiworld.get_locations(1)])


class TestFloorChecks5(DevilSpireTestBase):
    options = {"floor_checks": "every_5th"}

    def test_counts(self) -> None:
        self.assertEqual(len([l for l in self.multiworld.get_locations(1) if l.address]), 30)
        names = [l.name for l in self.multiworld.get_locations(1)]
        self.assertIn("Reach Floor -1", names)
        self.assertIn("Reach Floor -6", names)
        self.assertNotIn("Reach Floor -5", names)


class TestFloorChecks10(DevilSpireTestBase):
    options = {"floor_checks": "every_10th"}

    def test_counts(self) -> None:
        self.assertEqual(len([l for l in self.multiworld.get_locations(1) if l.address]), 20)
        names = [l.name for l in self.multiworld.get_locations(1)]
        self.assertIn("Reach Floor -11", names)
        self.assertNotIn("Reach Floor -10", names)
        self.collect_all_but([])
        self.assertBeatable(True)


class TestFloorChecksOff(DevilSpireTestBase):
    options = {"floor_checks": "off"}

    def test_counts(self) -> None:
        self.assertEqual(len([l for l in self.multiworld.get_locations(1) if l.address]), 10)
        self.assertEqual(len(self.multiworld.itempool), 10)
