# snake-python
My Snake implementation in Python for my kids.

# Map
The map has two dimensions: width and height. The (0, 0) coordinate is by the top left corner and the y axis is "upside-down".

```text
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
```
On the top there is a map represantation with 6 rows and 6 columns. In the game this can have different height and width values.

Map will not be represented with a matrix datastructure. I choose a different approach. Instead of storing a map representation in game, this script should calculate the
positions of each items (valuable, snake, etc) and calculate each movement. Later with an UI representation it can be shown as a grid, but in the background there should be no matrix for the map.