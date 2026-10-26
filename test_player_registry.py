#!/usr/bin/python3

import unittest

from player_registry import PlayerRegistry


class TestPlayerRegistry(unittest.TestCase):
    def test_init(self) -> None:
        pr = PlayerRegistry()
        self.assertDictEqual(pr.player_to_snake, {})

    def test_assign(self) -> None:
        pr = PlayerRegistry()

        pr.assign("player1", 2300)
        pr.assign("player2", 15201)

        self.assertEqual(pr.player_to_snake["player1"], 2300)
        self.assertEqual(pr.player_to_snake["player2"], 15201)

    def test_assign_same_player(self) -> None:
        pr = PlayerRegistry()
    
        pr.assign("player1", 2300)
        pr.assign("player2", 15201)
        pr.assign("player1", 2301)
    
        self.assertEqual(pr.player_to_snake["player1"], 2301)
        self.assertEqual(pr.player_to_snake["player2"], 15201)

    def test_resolve(self) -> None:
        pr = PlayerRegistry()
        
        pr.assign("player1", 2300)
        pr.assign("player2", 15201)

        sid1 = pr.resolve("player1")
        sid2 = pr.resolve("player2")
        sid3 = pr.resolve("player3")

        self.assertEqual(sid1, 2300)
        self.assertEqual(sid2, 15201)
        self.assertIsNone(sid3)

    def test_unassign(self) -> None:
        pr = PlayerRegistry()

        pr.assign("player1", 100)
        pr.unassign("player1")
        
        self.assertFalse("player1" in pr.player_to_snake.keys())
        self.assertIsNone(pr.player_to_snake.get("player1"))