#!/usr/bin/python3

import io
import unittest
from contextlib import redirect_stdout

from map import Map
from snake import Snake
from utils import Coordinate, Direction, TileType, Valuable


class MapTests(unittest.TestCase):
    def test_new_map_is_empty_and_out_of_bounds_are_walls(self):
        game_map = Map(3, 4)

        self.assertEqual(game_map.height, 3)
        self.assertEqual(game_map.width, 4)
        self.assertEqual(game_map.what_at(Coordinate(0, 0)), TileType.tile)
        for coordinate in (
            Coordinate(-1, 0),
            Coordinate(0, -1),
            Coordinate(4, 0),
            Coordinate(0, 3),
        ):
            with self.subTest(coordinate=coordinate):
                self.assertIs(game_map.what_at(coordinate), TileType.wall)

    def test_set_and_remove_valuable(self):
        game_map = Map(3, 4)
        valuable = Valuable(5)

        self.assertTrue(game_map.set_valuable(2, 1, valuable))
        self.assertIs(game_map.what_at(Coordinate(2, 1)), TileType.valuable)
        self.assertIs(game_map.remove_valuable(2, 1), valuable)
        self.assertIs(game_map.what_at(Coordinate(2, 1)), TileType.tile)

    def test_valuable_can_only_be_placed_on_empty_in_bounds_tile(self):
        game_map = Map(3, 4)
        original = Valuable(1)
        game_map.set_valuable(1, 1, original)

        self.assertFalse(game_map.set_valuable(1, 1, Valuable(2)))
        self.assertFalse(game_map.set_valuable(-1, 0, Valuable(3)))
        self.assertIs(game_map.valuables[Coordinate(1, 1)], original)

    def test_remove_missing_valuable_returns_none(self):
        game_map = Map(3, 4)

        self.assertIsNone(game_map.remove_valuable(1, 1))

    def test_set_snake_places_body_according_to_direction(self):
        expected_segments = {
            Direction.up: {Coordinate(3, 3), Coordinate(3, 4), Coordinate(3, 5)},
            Direction.down: {Coordinate(3, 3), Coordinate(3, 2), Coordinate(3, 1)},
            Direction.left: {Coordinate(3, 3), Coordinate(4, 3), Coordinate(5, 3)},
            Direction.right: {Coordinate(3, 3), Coordinate(2, 3), Coordinate(1, 3)},
        }

        for direction, expected in expected_segments.items():
            with self.subTest(direction=direction):
                game_map = Map(7, 7)

                self.assertTrue(
                    game_map.set_snake(Coordinate(3, 3), 12, Snake(3, direction))
                )
                self.assertSetEqual(game_map.snakes[12], expected)
                for coordinate in expected:
                    self.assertIs(game_map.what_at(coordinate), TileType.snake)

    def test_set_one_segment_snake(self):
        game_map = Map(3, 4)
        start = Coordinate(2, 1)

        self.assertTrue(game_map.set_snake(start, 7, Snake(1, Direction.up)))
        self.assertSetEqual(game_map.snakes[7], {start})

    def test_set_snake_fails_when_start_is_occupied(self):
        game_map = Map(4, 4)
        start = Coordinate(1, 1)
        game_map.set_valuable(start.x, start.y, Valuable(1))

        self.assertFalse(game_map.set_snake(start, 8, Snake(2, Direction.up)))
        self.assertNotIn(8, game_map.snakes)
        self.assertIs(game_map.what_at(start), TileType.valuable)

    def test_failed_snake_placement_rolls_back_partial_body(self):
        game_map = Map(3, 4)
        start = Coordinate(1, 1)
        first_segment = Coordinate(1, 0)

        self.assertFalse(game_map.set_snake(start, 9, Snake(3, Direction.down)))

        self.assertNotIn(9, game_map.snakes)
        self.assertIs(game_map.what_at(start), TileType.tile)
        self.assertIs(game_map.what_at(first_segment), TileType.tile)

    def test_failed_snake_placement_preserves_valuable(self):
        game_map = Map(5, 5)
        valuable_coordinate = Coordinate(2, 4)
        valuable = Valuable(2)
        game_map.set_valuable(valuable_coordinate.x, valuable_coordinate.y, valuable)

        self.assertFalse(
            game_map.set_snake(Coordinate(2, 2), 10, Snake(4, Direction.up))
        )

        self.assertNotIn(10, game_map.snakes)
        self.assertIs(game_map.what_at(valuable_coordinate), TileType.valuable)
        self.assertIs(game_map.valuables[valuable_coordinate], valuable)

    def test_prints_map_contents(self):
        game_map = Map(2, 3)
        game_map.set_valuable(1, 0, Valuable(1))
        game_map.set_snake(Coordinate(2, 1), 11, Snake(1, Direction.up))
        output = io.StringIO()

        with redirect_stdout(output):
            game_map.print()

        self.assertEqual(output.getvalue(), ". v .\n. . s\n")


if __name__ == "__main__":
    unittest.main()
