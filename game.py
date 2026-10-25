#!/usr/bin/python3


from collections import deque
import random
from typing import Optional
from map import Map
from snake import Snake
from utils import Coordinate, Direction, TileType, Valuable


class GameConfig:
    MAP_HEIGHT: int
    MAP_WIDTH: int
    NUMBER_OF_SNAKES: int
    MAX_NUMBER_OF_VALUABLES: int
    WRAPAROUND: bool
    MAX_TRY_COUNT: int
    INITIAL_SNAKE_LENGTH: Optional[int]

class Game:
    DEFAULT_SNAKE_LENGTH: int = 3

    def __init__(self, config: GameConfig, seed: Optional[int] = None):
        self.number_of_snakes: int = abs(config.NUMBER_OF_SNAKES)
        self.map_height: int = abs(config.MAP_HEIGHT)
        self.map_width: int = abs(config.MAP_WIDTH)
        self.number_of_valuables: int = abs(config.MAX_NUMBER_OF_VALUABLES)
        self.wraparound: bool = config.WRAPAROUND
        self.max_try_count: int = abs(config.MAX_TRY_COUNT)
        self.snakes: dict[int, Snake] = {}

        self.map = Map(self.map_height, self.map_width)

        self._rnd = random.Random(seed)

        snake_length: int = (
            config.INITIAL_SNAKE_LENGTH
            if config.INITIAL_SNAKE_LENGTH is not None
            else self.DEFAULT_SNAKE_LENGTH
        )

        self.palce_snake(snake_length)
        self.place_valuable()
        self.map.print()
    
    def place_valuable(self) -> None:
        for _ in range(0, self.number_of_valuables):
            v = Valuable(1)
            valuable_placed: bool = False
            try_count: int = 0
            while not valuable_placed:
                try_count += 1
                vX: int = random.randrange(0, self.map_width)
                vY: int = random.randrange(0, self.map_height)
                valuable_placed = self.map.set_valuable(vX, vY, v)
                if not valuable_placed and try_count >= self.max_try_count:
                    raise TimeoutError("Cannot place valuable int time. Check game config.")

    def palce_snake(self, snake_length: int) -> None:
        for i in range(0, self.number_of_snakes):
            self.snakes[i] = Snake(snake_length, Direction.down)
            snake_placed: bool = False
            try_count: int = 0
            while not snake_placed:
                try_count += 1
                sX: int = random.randrange(0, self.map_width - 1)
                sY: int = random.randrange(0, self.map_height - 1)
                snake_placed = self.map.set_snake(Coordinate(sX, sY), i, self.snakes[i])
                if not snake_placed and try_count >= self.max_try_count:
                    raise TimeoutError("Cannot place snake in time. Check game config.")

    def change_direction(self, snake_id: int, new_direction: Direction) -> None:
        if snake_id not in self.snakes.keys():
            return

        if self.snakes[snake_id].direction.opposite is new_direction:
            return

        if self.snakes[snake_id].direction is new_direction:
            return
        
        self.snakes[snake_id].direction = new_direction
        self.move_snake(snake_id)
    
    def move_snake(self, snake_id: int) -> None:
        if snake_id not in self.snakes.keys():
            return
        
        snake: Snake = self.snakes[snake_id]
        coords: deque[Coordinate] = self.map.snakes[snake_id]
        
        new_coord: Coordinate
        if snake.direction is Direction.up:
            new_coord = Coordinate(coords[0].x, coords[0].y - 1)
        elif snake.direction is Direction.down:
            new_coord = Coordinate(coords[0].x, coords[0].y + 1)
        elif snake.direction is Direction.left:
            new_coord = Coordinate(coords[0].x - 1, coords[0].y)
        elif snake.direction is Direction.right:
            new_coord = Coordinate(coords[0].x + 1, coords[0].y)
        else:
            raise ValueError(f"Invalid direction. Cannot move the snake {snake_id}.")

        tile = self.map.what_at(new_coord)
        if tile is TileType.wall and self.wraparound == False:
            self._remove_snake(snake_id)
            print("GAME OVER!")
            return
        # ToDo: Itt kitalálni a wraparound logikát ha fal a következő pont a térképen

        tail = coords[-1]
        will_grow_from_backlog = len(coords) < snake.length

        if tile is TileType.snake:
            if new_coord != tail or will_grow_from_backlog:
                self._remove_snake(snake_id)
                print("GAME OVER!")
                return
            else:
                hit_snake_id: Optional[int] = None
                for other_snake_id, other_coords in self.map.snakes.items():
                    if (snake_id != other_snake_id) and (new_coord in other_coords):
                        hit_snake_id = other_snake_id
                        break
                if hit_snake_id is not None:
                    self._remove_snake(hit_snake_id)
                    snake.consume_valuable(Valuable(2))

        v = self.map.remove_valuable(new_coord.x, new_coord.y)
        if v is not None:
            snake.consume_valuable(v)
        
        coords.appendleft(new_coord)
        if len(coords) > snake.length:
            coords.pop()

    def _remove_snake(self, snake_id: int) -> None:
        self.map.snakes.pop(snake_id)
        self.snakes.pop(snake_id)

if __name__ == "__main__":
    snakes: dict[int, Snake] = {}
    snakes[42] = Snake(5, Direction.right)
    print(snakes)
    print(snakes[42])

    snake = snakes[42]

    snake.consume_valuable(Valuable(3))
    snake.consume_valuable(Valuable(5))
    print(snakes)
    print(snakes[42])