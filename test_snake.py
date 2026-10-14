#!/usr/bin/python3

import unittest

from snake import Snake
from utils import Direction, Valuable

class SnakeTests(unittest.TestCase):
    def test_constructor_uses_up_when_direction_is_none(self):
        snake = Snake(3, None)

        self.assertEqual(snake.length, 3)
        self.assertIs(snake.direction, Direction.up)

    def test_constructor_uses_given_direction(self):
        snake = Snake(4, Direction.left)

        self.assertEqual(snake.length, 4)
        self.assertIs(snake.direction, Direction.left)

    def test_consume_valuable_increases_length(self):
        snake = Snake(3, Direction.up)

        snake.consume_valuable(Valuable(2))

        self.assertEqual(snake.length, 5)

    def test_consume_zero_value_does_not_change_length(self):
        snake = Snake(3, Direction.up)

        snake.consume_valuable(Valuable(0))

        self.assertEqual(snake.length, 3)

    def test_consume_negative_value_raises_without_changing_length(self):
        snake = Snake(3, Direction.up)

        with self.assertRaisesRegex(ValueError, "Value must be 0 or positive"):
            snake.consume_valuable(Valuable(-1))

        self.assertEqual(snake.length, 3)

    def test_set_direction_rejects_opposite_direction(self):
        for direction in Direction:
            with self.subTest(direction=direction):
                snake = Snake(3, direction)

                snake.set_direction(direction.opposite)

                self.assertIs(snake.direction, direction)

    def test_set_direction_accepts_same_or_perpendicular_direction(self):
        for direction in Direction:
            for new_direction in Direction:
                if new_direction is direction.opposite:
                    continue

                with self.subTest(direction=direction, new_direction=new_direction):
                    snake = Snake(3, direction)

                    snake.set_direction(new_direction)

                    self.assertIs(snake.direction, new_direction)
        