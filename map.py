#!/usr/bin/python3

from typing import Optional
from utils import Direction, TileType, Valuable, Coordinate
from snake import Snake

class Map:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.valuables: dict[Coordinate, Valuable] = {}
        self.snakes: dict[int, set[Coordinate]] = {}

    def set_valuable(self, pX: int, pY: int, v: Valuable) -> bool:
        coord = Coordinate(pX, pY)
        tile = self.what_at(coord)
        if tile == TileType.tile:
            self.valuables[coord] = v
            return True
        return False

    def _is_valuable(self, coordinate: Coordinate) -> bool:
        return coordinate in self.valuables

    def remove_valuable(self, pX: int, pY: int) -> Optional[Valuable]:
        coordinate = Coordinate(pX, pY)
        if self._is_valuable(coordinate):
            return self.valuables.pop(coordinate)
        return None

    def set_snake(self, start: Coordinate, snake_id: int, snake: Snake) -> bool:
        if self.what_at(start) != TileType.tile:
            return False
        
        self.snakes[snake_id] = set()
        self.snakes[snake_id].add(start)
        for i in range(0, snake.length - 1):
            if snake.direction == Direction.up:
                coord = Coordinate(start.x, start.y + i + 1)
                if not self._place_snake(snake_id, coord):
                    return False
            elif snake.direction == Direction.down:
                coord = Coordinate(start.x, start.y - i - 1)
                if not self._place_snake(snake_id, coord):
                    return False
            elif snake.direction == Direction.left:
                coord = Coordinate(start.x + i + 1, start.y)
                if not self._place_snake(snake_id, coord):
                    return False
            elif snake.direction == Direction.right:
                coord = Coordinate(start.x - i - 1, start.y)
                if not self._place_snake(snake_id, coord):
                    return False
            else:
                raise ValueError(f"Unknown direction: {snake.direction!r}")
        return True

    def _place_snake(self, snake_id: int, coord: Coordinate) -> bool:
        if self.what_at(coord) != TileType.tile:
            self.snakes.pop(snake_id)
            return False
        
        self.snakes[snake_id].add(coord)
        return True

    def _is_snake(self, coord: Coordinate) -> bool:
        return any(coord in snake_coordinates for snake_coordinates in self.snakes.values())

    def what_at(self, coordinate: Coordinate) -> TileType:
        if coordinate.y >= self.height or coordinate.y < 0:
            return TileType.wall
        elif coordinate.x >= self.width or coordinate.x < 0:
            return TileType.wall
        elif self._is_valuable(coordinate):
            return TileType.valuable
        elif self._is_snake(coordinate):
            return TileType.snake
        
        return TileType.tile

    def print(self) -> None:
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                coordinate = Coordinate(x, y)
                if self._is_valuable(coordinate):
                    row += " v"
                elif self.what_at(coordinate) == TileType.snake:
                    row += " s"
                else:
                    row += " ."
            row = row.strip(' ')
            print(row)


if __name__ == "__main__":
    map = Map(7, 6)

    snake = Snake(3, Direction.up)
    _ = map.set_snake(Coordinate(0 , 1), 42, snake)

    v1 = Valuable(1)
    v2 = Valuable(3)
    map.set_valuable(2, 4, v1)
    map.set_valuable(4, 0, v2)

    map.print()
