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
        self.assertAccessDependency(["Gauntlet cleared (Floor -99)", "Rhamdon defeated"], [[key_name(t) for t in range(9, 10)]])
        self.assertTrue(self.can_reach_region(tier_region_name(0)))


class TestOff(DevilSpireTestBase):
    options = {"floor_key_mode": "off"}

    def test_open(self) -> None:
        self.assertTrue(self.can_reach_location("Robot defeated (Floor -89)"))
        self.assertBeatable(True)


class TestStartDepthAndExtras(DevilSpireTestBase):
    options = {"starting_depth": 9, "trap_percentage": 100, "floor_milestones": True, "death_link": True}

    def test_open(self) -> None:
        self.assertBeatable(True)
        self.assertEqual(len(self.multiworld.get_locations(1)), 10 + 10 + 1)
