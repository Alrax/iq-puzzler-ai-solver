from typing import Literal, Tuple

NB_ROWS = 5
NB_COLS = 11

# Shape and color definitions for the pieces
PIECE_SHAPE = Tuple[Tuple[int, int], ...]
PIECE_COLOR = Literal[
    "yellow",
    "orange",
    "red",
    "burgundy",
    "pink",
    "purple",
    "dark_blue",
    "blue",
    "light_blue",
    "turquoise",
    "lime",
    "green",
    "empty"]

# Dimensions of each piece shape
PIECE_DIMENSIONS: dict[PIECE_COLOR, PIECE_SHAPE] = {
    "yellow": ((0, 0), (1, 0), (1, 1), (2, 0), (3, 0)),
    "orange": ((0, 0), (1, 0), (1, 1), (2, 0), (2, -1)),
    "red": ((0, 0), (1, 0), (1, 1), (1, 2), (1, 3)),
    "burgundy": ((0, 0), (0, 1), (1, 1), (1, 2)),
    "pink": ((0, 0), (1, 0), (1, 1), (2, 1), (3, 1)),
    "purple": ((0, 0), (1, 0), (1, 1), (2, 1), (2, 2)),
    "dark_blue": ((0, 0), (1, 0), (1, 1), (1, 2)),
    "blue": ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2)),
    "light_blue": ((0, 0), (1, 0), (1, 1)),
    "turquoise": ((0, 0), (0, 1), (1, 0), (1, 1), (1, 2)),
    "lime": ((0, 0), (0, 1), (1, 0), (2, 0), (2, 1)),
    "green": ((0, 0), (1, 0), (1, 1), (2, 0)),
    "empty": (),
}

# Numerical code for each piece color; 0 represents empty.
PIECE_CODES: dict[PIECE_COLOR, int] = {
    "empty": 0,
    "yellow": 1,
    "orange": 2,
    "red": 3,
    "burgundy": 4,
    "pink": 5,
    "purple": 6,
    "dark_blue": 7,
    "blue": 8,
    "light_blue": 9,
    "turquoise": 10,
    "lime": 11,
    "green": 12,
}
