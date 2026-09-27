#!/usr/bin/python3

from dataclasses import dataclass
from enum import Enum

@dataclass
class Valuable:
    value: int

@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int

class Direction(Enum):
    up = "up"
    down = "down"
    left = "left"
    right = "right"

    @property
    def opposite(self) -> "Direction":
        return {
            Direction.up: Direction.down,
            Direction.down: Direction.up,
            Direction.left: Direction.right,
            Direction.right: Direction.left,
        }[self]

class TileType(Enum):
    tile = "tile"
    snake = "snake"
    valuable = "valuable"
    wall = "wall"