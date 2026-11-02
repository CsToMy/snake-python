# snake-python

My Snake implementation in Python for my kids.

This project is also a small learning exercise in coding with AI assistance, so the code and this README evolve step by step as design decisions get made along the way.

# Status
## Part	State
Shared types (utils.py)	done
Snake (snake.py)	done
Map (map.py)	done
Game engine, config loading (game.py)	done
Player ID → snake ID mapping (player_registry.py)	done
Controller (game loop, input translation)	planned
UI	planned
Project structure
utils.py — shared types: Coordinate (immutable, hashable), Direction (with an opposite property), TileType, Valuable.
snake.py — the Snake class: holds a snake's own state (length, direction) and grows when it consumes a valuable. It does not know where it is on the map.
map.py — the Map class: owns the board and the positions of everything on it, and answers "what is at this position" queries.
game.py — GameConfig, load_config() and the Game class: the game engine that owns a Map and the Snake objects and applies the rules.
player_registry.py — PlayerRegistry: maps a UI-level player ID to a snake ID.
configs/ — JSON configuration files (e.g. default.json).
test_*.py — unit tests for each module.
# Architecture

Responsibilities are split so that each part has one reason to change:

UI  <->  Controller  <->  Game  ->  Map, Snake
              |
        PlayerRegistry
**Game** — the rules and the state. It knows nothing about any UI.
**Map** — spatial state only (where things are).
**Snake** — a single snake's own state (length, direction).
**PlayerRegistry** — which player controls which snake.
**Controller / UI** — not implemented yet. The controller will drive the game loop and translate raw input into Game calls; the UI will only render and capture input.

Configuration loading is a standalone function (load_config), deliberately not part of Game or GameConfig.

# Map

The map has two dimensions: width and height. The (0, 0) coordinate is at the top-left corner, and the y-axis is "upside-down" (increasing downward):

                                         x
                ------------------------→
                ┌───┬───┬───┬───┬───┬───┐
            │   │   │   │   │   │   │   │
            │   ├───┼───┼───┼───┼───┼───┤
            │   │   │   │   │   │   │   │
            │   ├───┼───┼───┼───┼───┼───┤
            │   │   │   │   │   │   │   │
            │   ├───┼───┼───┼───┼───┼───┤
            │   │   │   │   │   │   │   │
            │   ├───┼───┼───┼───┼───┼───┤
            │   │   │   │   │   │   │   │
            │   ├───┼───┼───┼───┼───┼───┤
            │   │   │   │   │   │   │   │
            ↓ y └───┴───┴───┴───┴───┴───┘

The example above shows a 6×6 map. In the game, width and height can be any values. Moving up decreases y, moving left decreases x.

No matrix, computed positions instead

The map is not represented with a matrix (2D array). Instead of storing a grid in memory, Map stores where things are and computes the answer to "what is at position (x, y)" on demand. A UI can later render this as a grid, but internally there is no matrix backing the map.

**Concretely, Map stores:**

- valuables: dict[Coordinate, Valuable] — the valuable placed at each coordinate (e.g. an apple).
- snakes: dict[int, deque[Coordinate]] — for each snake ID, the coordinates of its body in order: the first element is the head, the last is the tail. The order matters, because every body segment follows the one in front of it when the snake moves.

**What Map is responsible for**
- Spatial state. The single source of truth for what occupies which coordinate.
- Valuables. Placing and removing them on free tiles only.
- Placing snakes. Given a start coordinate, a snake ID and a Snake, the body is laid out behind the head (opposite to the facing direction) without wrapping around the edges. - If any tile is not free, the whole placement is rolled back and False is returned.
- Tile queries. what_at tells whether a coordinate is a wall (out of bounds), a valuable, a snake or an empty tile.
- Debug printing. A simple text view of the board.

What Map does not own: snake behavior (direction changes, movement rules) and snake ID assignment. IDs come from the caller and are only used as dictionary keys.

# Game
## Configuration

A GameConfig is an immutable (frozen) dataclass, usually loaded from JSON with load_config(path):

Field	Meaning
MAP_HEIGHT, MAP_WIDTH	size of the map
NUMBER_OF_SNAKES	how many snakes are placed at the start (at least 1)
MAX_NUMBER_OF_VALUABLES	how many valuables are placed at the start
WRAPAROUND	true: leaving the map on one side re-enters on the opposite side; false: walls are deadly
MAX_TRY_COUNT	how many random placement attempts are allowed before giving up
INITIAL_SNAKE_LENGTH	starting length, null for the default (3)

Example:

json
{
  "MAP_HEIGHT": 16,
  "MAP_WIDTH": 16,
  "NUMBER_OF_SNAKES": 1,
  "MAX_NUMBER_OF_VALUABLES": 1,
  "WRAPAROUND": false,
  "MAX_TRY_COUNT": 100,
  "INITIAL_SNAKE_LENGTH": null
}

load_config raises ValueError for an empty path or invalid JSON, IsADirectoryError if the path is a folder, FileNotFoundError if the file does not exist, and TypeError if fields are missing or unknown. Size and count values are made positive with abs(); NUMBER_OF_SNAKES = 0 becomes 1.

# Starting a game

Game(config, seed=None, snake_placed_listeners=None) places the snakes and valuables at random positions. A snake only starts in a direction in which it fits on the map (any direction when wraparound is on). If something cannot be placed within MAX_TRY_COUNT attempts, a TimeoutError is raised, which usually means the configuration is impossible (e.g. a map that is too small).

seed makes the random placement reproducible, which is what the tests use. The game has its own random generator and does not touch the global one.
snake_placed_listeners are callbacks that receive the snake ID of every snake as soon as it is placed. They have to be passed in the constructor, because the initial snakes are placed during construction. This is how a PlayerRegistry can learn the IDs. Later subscriptions are possible with on_snake_placed.
A turn
change_direction(snake_id, direction) only changes the direction. Unknown snake IDs, reversing into the opposite direction and repeating the current direction are ignored.
move_snakes() advances all snakes by one step at the same time.
Simultaneous movement

Moving the snakes one after another would be unfair: whoever is processed first would win every disputed cell. So move_snakes() works in phases:

Every snake's intended new head position is computed from the state at the beginning of the turn (including wraparound).
All collisions are resolved against that same starting state.
The surviving snakes move: the head advances, the tail follows.
Snakes that died are removed.

## Collision rules:

Wall (when WRAPAROUND is off): the snake dies.
Own body: the snake dies, except when it steps onto its own tail and that tail leaves the cell in the same turn.
Two heads onto the same cell: all of them die.
Two snakes swapping heads: both die.
Another snake's body: the snake that runs into it eats it — the victim is removed and the attacker grows by 2.
Another snake's tail that is just leaving its cell: safe, nothing happens.
Valuable: the snake grows by the valuable's value.

Growth is gradual: when a snake has to grow, its tail stays in place for the following turns until the snake reaches its new length.

## Game over

The game ends when no snake is left. on_game_over(callback) registers a callback that is called exactly once at that moment. After the game is over, the Game object ignores any further moves, direction changes and valuable placements, so nothing can change in it anymore. Starting a new game means creating a new Game object.

## Players

PlayerRegistry maps a player ID chosen by the UI layer (for example "player_1") to the ID of a snake. Looking up an unknown player returns None, which the controller treats as "ignore this input". This way the UI only has to say which player pressed a key, and the same mapping covers local multiplayer with several players on one machine.

## Running the tests
pytest

**With coverage:**

pytest --cov=. --cov-report=term-missing

The tests can also be run with python -m unittest. The GitHub Actions workflow runs flake8 and the test suite on every push and pull request.

## Not done yet
Controller: game loop, timing, translating UI input into Game calls and forwarding game events to the UI.
UI.
Valuables are only placed at the start; eaten ones are not replaced yet.
No separate "win" condition: the game simply ends when no snake is left.