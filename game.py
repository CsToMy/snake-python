#!/usr/bin/python3


from collections import deque
from dataclasses import dataclass
import random
from typing import Callable, Optional
from map import Map
from snake import Snake
from utils import Coordinate, Direction, TileType, Valuable


@dataclass
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
        self._game_over: bool = False
        self._game_over_listeners: list[Callable[[], None]] = []

        snake_length: int = (
            config.INITIAL_SNAKE_LENGTH
            if config.INITIAL_SNAKE_LENGTH is not None
            else self.DEFAULT_SNAKE_LENGTH
        )

        self.place_snake(snake_length)
        for _ in range(0, self.number_of_valuables):
            self.place_valuable()
        self.map.print()

    @property
    def is_game_over(self) -> bool:
        return self._game_over
    
    def place_valuable(self) -> None:
        if self._game_over:
            return
        
        v = Valuable(1)
        valuable_placed: bool = False
        try_count: int = 0
        while not valuable_placed:
            try_count += 1
            vX: int = self._rnd.randrange(0, self.map_width)
            vY: int = self._rnd.randrange(0, self.map_height)
            valuable_placed = self.map.set_valuable(vX, vY, v)
            if not valuable_placed and try_count >= self.max_try_count:
                raise TimeoutError("Cannot place valuable in time. Check game config.")

    def place_snake(self, snake_length: int) -> None:
        if self._game_over:
            return
        
        for i in range(0, self.number_of_snakes):
            self.snakes[i] = Snake(snake_length, Direction.down)
            snake_placed: bool = False
            try_count: int = 0
            while not snake_placed:
                try_count += 1
                sX: int = self._rnd.randrange(0, self.map_width - 1)
                sY: int = self._rnd.randrange(0, self.map_height - 1)
                snake_placed = self.map.set_snake(Coordinate(sX, sY), i, self.snakes[i])
                if not snake_placed and try_count >= self.max_try_count:
                    raise TimeoutError("Cannot place snake in time. Check game config.")

    def on_game_over(self, callback: Callable[[], None]) -> None:
        self._game_over_listeners.append(callback)

    def _end_game(self)-> None:
        if self._game_over:
            return
        self._game_over = True
        for listener in self._game_over_listeners:
            listener()
    
    def change_direction(self, snake_id: int, new_direction: Direction) -> None:
        if self._game_over:
            return
        
        if snake_id not in self.snakes.keys():
            return

        if self.snakes[snake_id].direction.opposite is new_direction:
            return

        if self.snakes[snake_id].direction is new_direction:
            return
        
        self.snakes[snake_id].direction = new_direction
        self.move_snake(snake_id)
    
    def move_snake(self, snake_id: int) -> None:
        if self._game_over:
            return
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

        if self.wraparound:
            new_coord = Coordinate(new_coord.x % self.map_width, new_coord.y % self.map_height)
        
        tile = self.map.what_at(new_coord)
        if tile is TileType.wall and self.wraparound == False:
            self._remove_snake(snake_id)
            return

        tail = coords[-1]
        will_grow_from_backlog = len(coords) < snake.length

        if tile is TileType.snake:
            if new_coord in coords:
                if new_coord != tail or will_grow_from_backlog:
                    self._remove_snake(snake_id)
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
        if self._game_over:
            return
        
        self.map.snakes.pop(snake_id)
        self.snakes.pop(snake_id)
        if not self.snakes:
            self._end_game()

if __name__ == "__main__":
    print("Game")