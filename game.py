#!/usr/bin/python3


from dataclasses import dataclass
import json
import os
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

    def __init__(
            self,
            config: GameConfig,
            seed: Optional[int] = None,
            snake_placed_listeners: Optional[list[Callable[[int], None]]] = None
            ) -> None:
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
        self._snake_placed_listeners: list[Callable[[int], None]] = (
            list(snake_placed_listeners) if snake_placed_listeners else []
        )

        snake_length: int = (
            config.INITIAL_SNAKE_LENGTH
            if config.INITIAL_SNAKE_LENGTH is not None
            else self.DEFAULT_SNAKE_LENGTH
        )

        for snake_id in range(self.number_of_snakes):
            self.place_snake(snake_id, snake_length)
            for listener in self._snake_placed_listeners:
                listener(snake_id)

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

    def on_snake_placed(self, callback: Callable[[int], None]) -> None:
        self._snake_placed_listeners.append(callback)

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

    def _remove_snake(self, snake_id: int) -> None:
        if self._game_over:
            return
        
        self.map.snakes.pop(snake_id)
        self.snakes.pop(snake_id)
        if not self.snakes:
            self._end_game()

    def _find_snake_at(
            self, coord: Coordinate, candidates: list[int], exclude: Optional[int] = None
        ) -> Optional[int]:
            for snake_id in candidates:
                if snake_id == exclude:
                    continue
                if coord in self.map.snakes.get(snake_id, ()):
                    return snake_id
            return None
    
    def move_snakes(self) -> None:
        if self._game_over:
            return

        living_ids = list(self.snakes.keys())
        intents: dict[int, Coordinate] = {}
        tail_vacates: dict[int, bool] = {}

        # where will the snake be?
        # will it grow? 
        for snake_id in living_ids:
            snake = self.snakes[snake_id]
            coords = self.map.snakes[snake_id]
            head = coords[0]

            if snake.direction is Direction.up:
                new_head = Coordinate(head.x, head.y - 1)
            elif snake.direction is Direction.down:
                new_head = Coordinate(head.x, head.y + 1)
            elif snake.direction is Direction.left:
                new_head = Coordinate(head.x - 1, head.y)
            elif snake.direction is Direction.right:
                new_head = Coordinate(head.x + 1, head.y)
            else:
                raise ValueError(f"Invalid direction. Cannot move the snake {snake_id}.")

            if self.wraparound:
                new_head = Coordinate(new_head.x % self.map_width, new_head.y % self.map_height)

            intents[snake_id] = new_head
            eats_valuable = new_head in self.map.valuables
            will_grow_from_backlog = len(coords) < snake.length
            tail_vacates[snake_id] = not (will_grow_from_backlog or eats_valuable)

        # start checking for collisions
        dead: set[int] = set()
        eaten_by: dict[int, int] = {}  # attacker_id -> victim_id

        # hit wall
        for snake_id, new_head in intents.items():
            if not self.wraparound and self.map.what_at(new_head) is TileType.wall:
                dead.add(snake_id)

        targets: dict[Coordinate, list[int]] = {}
        for snake_id, new_head in intents.items():
            targets.setdefault(new_head, []).append(snake_id)
        for colliding_ids in targets.values():
            if len(colliding_ids) > 1:
                dead.update(colliding_ids)

        for snake_id in living_ids:
            if snake_id in dead:
                continue
            a_head_now = self.map.snakes[snake_id][0]
            other_snake_id = self._find_snake_at(intents[snake_id], living_ids)
            if (
                other_snake_id is not None
                and other_snake_id != snake_id
                and intents.get(other_snake_id) == a_head_now
            ):
                dead.add(snake_id)
                dead.add(other_snake_id)

        for snake_id in living_ids:
            if snake_id in dead:
                continue
            new_head = intents[snake_id]
            own_coords = self.map.snakes[snake_id]

            if new_head in own_coords:
                if new_head != own_coords[-1] or not tail_vacates[snake_id]:
                    dead.add(snake_id)
                continue

            other_id = self._find_snake_at(new_head, living_ids, exclude=snake_id)
            if other_id is not None and other_id not in dead:
                other_coords = self.map.snakes[other_id]
                if new_head == other_coords[-1] and tail_vacates[other_id]:
                    continue
                eaten_by[snake_id] = other_id
                dead.add(other_id)

        for snake_id in living_ids:
            if snake_id in dead:
                continue

            snake = self.snakes[snake_id]
            coords = self.map.snakes[snake_id]
            new_head = intents[snake_id]

            if snake_id in eaten_by:
                snake.consume_valuable(Valuable(2))

            v = self.map.remove_valuable(new_head)
            if v is not None:
                snake.consume_valuable(v)

            coords.appendleft(new_head)
            if len(coords) > snake.length:
                coords.pop()

        for snake_id in list(dead):
            self._remove_snake(snake_id)



def load_config(path: str) -> GameConfig:
    if path == "":
        raise ValueError("Configuration path cannot be empty.")
    if os.path.isdir(path):
        raise IsADirectoryError(f"Configuration path is a folder: {path}")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file does not exist: {path}")

    with open(path, "r", encoding="utf-8") as config_file:
        config = GameConfig(**json.load(config_file))
    return config

if __name__ == "__main__":
    print("Game")