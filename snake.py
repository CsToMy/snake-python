#!/usr/bin/python3

from typing import Optional
from utils import Valuable, Direction

class Snake:
    def __init__(self, length: int, direction: Optional[Direction]):
        self.length: int = length
        self.direction: Direction = direction if direction is not None else Direction.up

    def consume_valuable(self, v: Valuable) -> None:
        if v.value < 0:
            raise ValueError("Value must be 0 or positive.")
        self.length += v.value

    def set_direction(self, new_direction: Direction) -> None:
        if self.direction.opposite != new_direction:
            self.direction = new_direction

    def __str__(self) -> str:
        return f"Snake: l = {self.length}, d = {self.direction.name}"
