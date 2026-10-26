#!/usr/bin/python3

from typing import Optional


class PlayerRegistry:
    def __init__(self) -> None:
        self.player_to_snake: dict[str, int] = {}

    def assign(self, player_id: str, snake_id:int) -> None:
        self.player_to_snake[player_id] = snake_id

    def resolve(self, player_id: str) -> Optional[int]:
        return self.player_to_snake.get(player_id)

    def unassign(self, player_id: str) -> None:
        if player_id in self.player_to_snake.keys():
            self.player_to_snake.pop(player_id)
        return