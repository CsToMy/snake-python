#!/usr/bin/python3


import random
from map import Map
from snake import Snake
from utils import Coordinate, Direction, Valuable


class Game:
    def __init__(self):
        self.number_of_snakes: int = 1
        self.map_height: int = 10
        self.map_width: int = 10
        self.number_of_valuables: int = 1
        self.snakes: dict[int, Snake] = {}

        self.map = Map(self.map_height, self.map_width)

        for i in range(0, self.number_of_snakes):
            self.snakes[i] = Snake(3, Direction.down)

            snake_placed: bool = False
            while not snake_placed:
                sX: int = random.randrange(0, self.map_width)
                sY: int = random.randrange(0, self.map_height)
                snake_placed = self.map.set_snake(Coordinate(sX, sY), i, self.snakes[i])

        self.place_valuable()
        

    def change_direction(self, snake_id: int, new_direction: Direction) -> None:
        pass

    def _is_collide(self, snake_id: int) -> bool:
        return False

    def place_valuable(self) -> None:
        for _ in range(0, self.number_of_valuables):
            v = Valuable(1)
            valuable_placed: bool = False
            while not valuable_placed:
                vX: int = random.randrange(0, self.map_width)
                vY: int = random.randrange(0, self.map_height)
                valuable_placed = self.map.set_valuable(vX, vY, v)
