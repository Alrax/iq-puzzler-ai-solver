"""Game logic package: board state and piece constants."""
from .board import Board
from .constants import (
    NB_ROWS,
    NB_COLS,
    PIECE_DIMENSIONS,
    PIECE_CODES,
    PIECE_COLOR,
)

__all__ = [
    "Board",
    "NB_ROWS",
    "NB_COLS",
    "PIECE_DIMENSIONS",
    "PIECE_CODES",
    "PIECE_COLOR",
]
