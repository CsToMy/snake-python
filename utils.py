#!/usr/bin/python3

from dataclasses import dataclass
from enum import Enum

@dataclass
class Valuable:
    value: int

@dataclass
class Coordinate:
    x: int
    y: int

class Direction(Enum):
    up = "up"
    down = "down"
    left = "left"
    right = "right"

