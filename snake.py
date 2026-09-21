#!/usr/bin/python3

from utils import Valuable, Coordinate, Direction

class Snake:
    def __init__(self, lenght: int):
        self.lenght = lenght
        self.coordinates: list[Coordinate] = []

    def consume_valuable(self, v: Valuable) -> None:
        self.lenght += v.value

    def place(self, start: Coordinate, direction: Direction) -> None:
        self.coordinates.append(start)

        if direction == Direction.up:
            for i in range(1, self.lenght):
                self.coordinates.append(Coordinate(start.x, start.y + i))
        elif direction == Direction.down:
            for i in range(1, self.lenght):
                self.coordinates.append(Coordinate(start.x, start.y - i))
        elif direction == Direction.left:
            for i in range(1, self.lenght):
                self.coordinates.append(Coordinate(start.x + i, start.y))
        else:
            for i in range(1, self.lenght):
                self.coordinates.append(Coordinate(start.x - i, start.y))