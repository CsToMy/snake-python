#!/usr/bin/python3

import json
import os
import tempfile
from typing import Any
import unittest

from game import GameConfig, load_config


class TestLoadConfig(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _write_config(self, filename: str, content: dict[str, Any]) -> str:
        path = os.path.join(self.tmp_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(content, f)
        return path

    def test_empty_path(self) -> None:
        path = ""
        with self.assertRaises(ValueError):
            load_config(path)

    def test_folder_path(self) -> None:
        with self.assertRaises(IsADirectoryError):
            load_config(self.tmp_dir)

    def test_not_exists_path(self) -> None:
        path = os.path.join(self.tmp_dir,"DOES_NOT_EXISTS.json")
        with self.assertRaises(FileNotFoundError):
            load_config(path)

    def test_malformed_json_raises(self) -> None:
        path = os.path.join(self.tmp_dir, "broken.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write("{invalid json")

        with self.assertRaises(ValueError):
            load_config(path)

    def test_missing_field(self) -> None:
        path = self._write_config("missing_field.json", {
            "MAP_HEIGHT": 10,
            "MAP_WIDTH": 10,
            "MAX_NUMBER_OF_VALUABLES": 1,
            "WRAPAROUND": False,
            "MAX_TRY_COUNT": 100,
            "INITIAL_SNAKE_LENGTH": 3,
        })

        with self.assertRaises(TypeError):
            load_config(path)

    def test_valid_config_loads(self) -> None:
        path = self._write_config("valid.json", {
            "MAP_HEIGHT": 21,
            "MAP_WIDTH": 17,
            "NUMBER_OF_SNAKES": 3,
            "MAX_NUMBER_OF_VALUABLES": 1,
            "WRAPAROUND": False,
            "MAX_TRY_COUNT": 100,
            "INITIAL_SNAKE_LENGTH": 3,
        })

        config = load_config(path)

        self.assertIsInstance(config, GameConfig)
        self.assertEqual(config.MAP_HEIGHT, 21)
        self.assertEqual(config.MAP_WIDTH, 17)
        self.assertEqual(config.NUMBER_OF_SNAKES, 3)
        self.assertEqual(config.MAX_NUMBER_OF_VALUABLES, 1)
        self.assertEqual(config.WRAPAROUND, False)
        self.assertEqual(config.MAX_TRY_COUNT, 100)
        self.assertEqual(config.INITIAL_SNAKE_LENGTH, 3)

if __name__ == "__main__":
    unittest.main()