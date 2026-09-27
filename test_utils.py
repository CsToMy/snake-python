import unittest

from utils import Direction


class DirectionTest(unittest.TestCase):
    def test_members_and_values(self):
        self.assertEqual(
            list(Direction),
            [Direction.up, Direction.down, Direction.left, Direction.right],
        )
        self.assertEqual(
            [direction.value for direction in Direction],
            ["up", "down", "left", "right"],
        )

    def test_opposite_directions(self):
        expected_opposites = {
            Direction.up: Direction.down,
            Direction.down: Direction.up,
            Direction.left: Direction.right,
            Direction.right: Direction.left,
        }

        for direction, expected_opposite in expected_opposites.items():
            with self.subTest(direction=direction):
                self.assertIs(direction.opposite, expected_opposite)

    def test_opposite_is_involution(self):
        for direction in Direction:
            with self.subTest(direction=direction):
                self.assertIs(direction.opposite.opposite, direction)


if __name__ == "__main__":
    unittest.main()