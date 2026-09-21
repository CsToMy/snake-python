#!/usr/bin/python3

import random
from typing import Optional
from utils import Valuable, Coordinate, Direction
from snake import Snake

class Map:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.valuables: dict[tuple[int, int], Valuable] = {}
        self.snakes: list[Snake] = []

    def set_valuable(self, pX: int, pY: int, v: Valuable) -> bool:
        if not self.is_valuable(pX, pY):
            self.valuables[(pX, pY)] = v
            return True
        return False

    def set_valuable_random(self, v: Valuable) -> None:
        is_placed = False
        while not is_placed:
            pX = random.randrange(self.width)
            pY = random.randrange(self.height)
            is_placed = self.set_valuable(pX, pY, v)

    def is_valuable(self, pX: int, pY: int) -> bool:
        return (pX, pY) in self.valuables.keys()

    def remove_valuable(self, pX: int, pY: int) -> Optional[Valuable]:
        if self.is_valuable(pX, pY):
            return self.valuables.pop((pX, pY))
        return None

    def set_snake(self, start: Coordinate, snake: Snake) -> bool:
        is_placed = False
        direction = Direction.up
        while not is_placed:
            direction = random.choice((Direction.up, Direction.down, Direction.left, Direction.right))
            if direction == Direction.up:
                is_placed = (start.y - snake.lenght) >= 0
            elif direction == Direction.down:
                is_placed = (start.y + snake.lenght) < self.height
            elif direction == Direction.left:
                is_placed = (start.x + snake.lenght) < self.width
            else:
                is_placed = (start.x - snake.lenght) >= 0
        
        snake.place(start, direction)
        self.snakes.append(snake)
        return is_placed

    def set_snake_random(self, snake: Snake) -> None:
        is_placed = False
        while not is_placed:
            pX = random.randrange(self.width)
            pY = random.randrange(self.height)
            is_placed = self.set_snake(Coordinate(pX, pY), snake)
