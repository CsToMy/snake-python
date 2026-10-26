#!/usr/bin/python3


from collections import deque
from dataclasses import dataclass
import random
from typing import Callable, Optional
from map import Map
from snake import Snake
from utils import Coordinate, Direction, TileType, Valuable


@dataclass(frozen=True)
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
        self.number_of_snakes: int = abs(config.NUMBER_OF_SNAKES) or 1
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

        for snake_id in range(self.number_of_snakes):
            self.place_snake(snake_id, snake_length)

        for _ in range(self.number_of_valuables):
            self.place_valuable()
        
        self.map.print()

    @property
    def is_game_over(self) -> bool:
        return self._game_over
    
    def place_valuable(self) -> None:
        if self._game_over:
            return
        v = Valuable(1)
        self._place_with_retry(lambda x, y: self.map.set_valuable(Coordinate(x, y), v), "valuable")

    def place_snake(self, snake_id: int, snake_length: int) -> None:
        if self._game_over:
            return

        try_count = 0
        while True:
            try_count += 1
            x = self._rnd.randrange(0, self.map_width)
            y = self._rnd.randrange(0, self.map_height)
            pos = Coordinate(x, y)
            valid_directions = self._valid_start_directions(pos, snake_length)
            if valid_directions:
                direction = self._rnd.choice(valid_directions)
                self.snakes[snake_id] = Snake(snake_length, direction)
                if self.map.set_snake(pos, snake_id, self.snakes[snake_id]):
                    return
                del self.snakes[snake_id]
            if try_count >= self.max_try_count:
                raise TimeoutError("Cannot place snake in time. Check game config.")
    
    def _place_with_retry(self, place_fn: Callable[[int, int], bool], what: str) -> None:
        try_count = 0
        while True:
            try_count += 1
            x = self._rnd.randrange(0, self.map_width)
            y = self._rnd.randrange(0, self.map_height)
            if place_fn(x, y):
                return
            if try_count >= self.max_try_count:
                raise TimeoutError(f"Cannot place {what} in time. Check game config.")

    def _valid_start_directions(self, pos: Coordinate, length: int) -> list[Direction]:
        if self.wraparound:
            return list(Direction)
        
        valid: list[Direction] = []
        if pos.x - (length - 1) >= 0:
            valid.append(Direction.right)
        if pos.x + (length - 1) < self.map_width:
            valid.append(Direction.left)
        if pos.y - (length - 1) >= 0:
            valid.append(Direction.down)
        if pos.y + (length - 1) < self.map_height:
            valid.append(Direction.up)
        return valid
    
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
        if tile is TileType.wall:
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

        v = self.map.remove_valuable(new_coord)
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