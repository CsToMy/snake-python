#!/usr/bin/python3

import contextlib
import dataclasses
import io
from typing import Any
import unittest
from collections import deque

from game import Game, GameConfig
from snake import Snake
from utils import Coordinate, Direction, TileType, Valuable


class TestGame(unittest.TestCase):
    def _make_game(self, **overrides: Any) -> Game:
        defaults: dict[str, Any] = dict(
            MAP_HEIGHT=10,
            MAP_WIDTH=10,
            NUMBER_OF_SNAKES=1,
            MAX_NUMBER_OF_VALUABLES=0,
            WRAPAROUND=False,
            MAX_TRY_COUNT=100,
            INITIAL_SNAKE_LENGTH=3,
        )
        defaults.update(overrides)
        config = GameConfig(**defaults)
        with contextlib.redirect_stdout(io.StringIO()):
            return Game(config, seed=1)

    def test_creation(self) -> None:
        game = self._make_game(NUMBER_OF_SNAKES=2, MAX_NUMBER_OF_VALUABLES=2)

        self.assertFalse(game.is_game_over)
        self.assertEqual(len(game.snakes), 2)
        self.assertEqual(len(game.map.snakes), 2)
        self.assertEqual(len(game.map.valuables), 2)

        for snake_id, snake in game.snakes.items():
            self.assertEqual(snake.length, 3)
            coords = game.map.snakes[snake_id]
            self.assertEqual(len(coords), 3)
            for c in coords:
                self.assertTrue(0 <= c.x < game.map_width)
                self.assertTrue(0 <= c.y < game.map_height)

    def test_snake_placement(self) -> None:
        game = self._make_game(INITIAL_SNAKE_LENGTH=5)
        coords = list(game.map.snakes[0])

        self.assertEqual(len(coords), 5)
        self.assertEqual(len(set(coords)), 5)

        for a, b in zip(coords, coords[1:]):
            manhattan_distance = abs(a.x - b.x) + abs(a.y - b.y)
            self.assertEqual(manhattan_distance, 1)

    def test_place_valuable(self) -> None:
        game = self._make_game(MAX_NUMBER_OF_VALUABLES=0)
        self.assertEqual(len(game.map.valuables), 0)

        game.place_valuable()

        self.assertEqual(len(game.map.valuables), 1)
        coord, valuable = next(iter(game.map.valuables.items()))
        self.assertEqual(game.map.what_at(coord), TileType.valuable)
        self.assertEqual(valuable.value, 1)

    def test_change_direction(self) -> None:
        game = self._make_game()
        snake = game.snakes[0]
        original = snake.direction
        perpendicular = (
            Direction.left if original in (Direction.up, Direction.down) else Direction.up
        )

        game.change_direction(0, original.opposite)
        self.assertIs(snake.direction, original)

        game.change_direction(0, perpendicular)
        self.assertIs(snake.direction, perpendicular)

    def test_move_snake(self) -> None:
        game = self._make_game(MAX_NUMBER_OF_VALUABLES=0)
        sid = 0
        game.snakes[sid] = Snake(3, Direction.right)
        game.map.snakes[sid] = deque(
            [Coordinate(5, 5), Coordinate(4, 5), Coordinate(3, 5)]
        )

        game.move_snake(sid)

        coords = game.map.snakes[sid]
        self.assertEqual(coords[0], Coordinate(6, 5))
        self.assertEqual(len(coords), 3)
        self.assertNotIn(Coordinate(3, 5), coords)

    def test_remove_snake(self) -> None:
        game = self._make_game(NUMBER_OF_SNAKES=2)
        self.assertIn(0, game.snakes)
        self.assertIn(0, game.map.snakes)

        game._remove_snake(0) # pyright: ignore[reportPrivateUsage]

        self.assertNotIn(0, game.snakes)
        self.assertNotIn(0, game.map.snakes)
        self.assertFalse(game.is_game_over)

        game._remove_snake(1) # pyright: ignore[reportPrivateUsage]
        self.assertTrue(game.is_game_over)

    def test_self_collidion(self) -> None:
        sid = 0

        game1 = self._make_game(MAX_NUMBER_OF_VALUABLES=0)
        game1.snakes[sid] = Snake(4, Direction.right)
        game1.map.snakes[sid] = deque(
            [Coordinate(5, 5), Coordinate(6, 5), Coordinate(6, 6), Coordinate(5, 6)]
        )

        game1.move_snake(sid)

        self.assertTrue(game1.is_game_over)
        self.assertNotIn(sid, game1.snakes)

        game2 = self._make_game(MAX_NUMBER_OF_VALUABLES=0)
        game2.snakes[sid] = Snake(4, Direction.right)
        game2.map.snakes[sid] = deque(
            [Coordinate(2, 2), Coordinate(2, 3), Coordinate(3, 3), Coordinate(3, 2)]
        )

        game2.move_snake(sid)

        self.assertFalse(game2.is_game_over)
        self.assertEqual(game2.map.snakes[sid][0], Coordinate(3, 2))
        self.assertEqual(len(game2.map.snakes[sid]), 4)

    def test_collide_with_other_snake(self) -> None:
        game = self._make_game(NUMBER_OF_SNAKES=2, MAX_NUMBER_OF_VALUABLES=0)
        attacker_id, victim_id = 0, 1

        game.snakes[attacker_id] = Snake(3, Direction.right)
        game.map.snakes[attacker_id] = deque(
            [Coordinate(4, 5), Coordinate(3, 5), Coordinate(2, 5)]
        )
        game.snakes[victim_id] = Snake(3, Direction.up)
        game.map.snakes[victim_id] = deque(
            [Coordinate(5, 4), Coordinate(5, 5), Coordinate(5, 6)]
        )

        length_before = game.snakes[attacker_id].length
        game.move_snake(attacker_id)

        self.assertNotIn(victim_id, game.snakes)
        self.assertNotIn(victim_id, game.map.snakes)
        self.assertIn(attacker_id, game.snakes)

        self.assertEqual(game.snakes[attacker_id].length, length_before + 2)

    def test_consume_valuable(self) -> None:
        game = self._make_game(MAX_NUMBER_OF_VALUABLES=0)
        sid = 0
        game.snakes[sid] = Snake(3, Direction.right)
        game.map.snakes[sid] = deque(
            [Coordinate(4, 5), Coordinate(3, 5), Coordinate(2, 5)]
        )
        game.map.set_valuable(5, 5, Valuable(2))

        length_before = game.snakes[sid].length
        game.move_snake(sid)

        self.assertEqual(game.snakes[sid].length, length_before + 2)
        self.assertNotIn(Coordinate(5, 5), game.map.valuables)
        self.assertEqual(len(game.map.snakes[sid]), 4)

    def test_win_the_game(self) -> None:
        game = self._make_game(NUMBER_OF_SNAKES=2)

        game._remove_snake(0) # pyright: ignore[reportPrivateUsage]

        self.assertFalse(game.is_game_over)
        self.assertEqual(list(game.snakes.keys()), [1])

    def test_has_game_ended(self) -> None:
        game = self._make_game(NUMBER_OF_SNAKES=1)
        calls: list[int] = []
        game.on_game_over(lambda: calls.append(1))

        self.assertFalse(game.is_game_over)

        game._remove_snake(0) # pyright: ignore[reportPrivateUsage]

        self.assertTrue(game.is_game_over)
        self.assertEqual(len(calls), 1)

        game._remove_snake(0) # pyright: ignore[reportPrivateUsage]
        self.assertEqual(len(calls), 1)


    def test_move_snake_wall_collision(self) -> None:
        game = self._make_game(
            MAP_WIDTH=10, MAP_HEIGHT=10, WRAPAROUND=False, MAX_NUMBER_OF_VALUABLES=0
        )
        sid = 0
        game.snakes[sid] = Snake(3, Direction.right)
        game.map.snakes[sid] = deque(
            [Coordinate(9, 5), Coordinate(8, 5), Coordinate(7, 5)]
        )

        game.move_snake(sid)

        self.assertTrue(game.is_game_over)
        self.assertNotIn(sid, game.snakes)
        self.assertNotIn(sid, game.map.snakes)

    def test_wraparound_teleports_through_wall(self) -> None:
        game = self._make_game(
            MAP_WIDTH=10, MAP_HEIGHT=10, WRAPAROUND=True, MAX_NUMBER_OF_VALUABLES=0
        )
        sid = 0
        game.snakes[sid] = Snake(3, Direction.right)
        game.map.snakes[sid] = deque(
            [Coordinate(9, 5), Coordinate(8, 5), Coordinate(7, 5)]
        )

        game.move_snake(sid)

        self.assertFalse(game.is_game_over)
        self.assertIn(sid, game.snakes)
        self.assertEqual(game.map.snakes[sid][0], Coordinate(0, 5))

    def test_unknown_snake_id_is_noop(self) -> None:
        game = self._make_game()
        snakes_before = dict(game.snakes)
        map_before = {k: list(v) for k, v in game.map.snakes.items()}

        game.move_snake(999)
        game.change_direction(999, Direction.up)

        self.assertEqual(game.snakes.keys(), snakes_before.keys())
        for sid, coords in map_before.items():
            self.assertEqual(list(game.map.snakes[sid]), coords)

    def test_actions_are_noop_after_game_over(self) -> None:
        game = self._make_game(NUMBER_OF_SNAKES=1, MAX_NUMBER_OF_VALUABLES=0)
        sid = 0
        game._remove_snake(sid) # pyright: ignore[reportPrivateUsage]
        self.assertTrue(game.is_game_over)

        snakes_before = dict(game.snakes)
        valuables_before = dict(game.map.valuables)

        game.move_snake(sid)
        game.change_direction(sid, Direction.up)
        game.place_valuable()

        self.assertEqual(game.snakes, snakes_before)
        self.assertEqual(game.map.valuables, valuables_before)

    def test_place_snake_raises_timeout_when_impossible(self) -> None:
        with self.assertRaises(TimeoutError):
            self._make_game(
                MAP_WIDTH=1,
                MAP_HEIGHT=1,
                NUMBER_OF_SNAKES=1,
                INITIAL_SNAKE_LENGTH=3,
                MAX_TRY_COUNT=5,
            )

    def test_config_defaults_and_sanitization(self) -> None:
        game = self._make_game(
            NUMBER_OF_SNAKES=0,
            MAP_HEIGHT=-10,
            MAP_WIDTH=-10,
            INITIAL_SNAKE_LENGTH=None,
        )

        self.assertEqual(game.map_height, 10)
        self.assertEqual(game.map_width, 10)
        self.assertEqual(len(game.snakes), 1)
        self.assertEqual(
            next(iter(game.snakes.values())).length, Game.DEFAULT_SNAKE_LENGTH
        )

    def test_config_is_immutable(self) -> None:
        config = GameConfig(
            MAP_HEIGHT=10,
            MAP_WIDTH=10,
            NUMBER_OF_SNAKES=1,
            MAX_NUMBER_OF_VALUABLES=0,
            WRAPAROUND=False,
            MAX_TRY_COUNT=100,
            INITIAL_SNAKE_LENGTH=3,
        )

        with self.assertRaises(dataclasses.FrozenInstanceError):
            config.MAP_HEIGHT = 99  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()