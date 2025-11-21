from constants import *

class Board:
    """Board backed by a 2D list of ints (piece codes). 0 = empty.

    Placement uses rotation only (0,90,180,270 clockwise). 
    Signature:
        place_piece(color, origin_row, origin_col, rotation)
    """

    def __init__(self):
        self.nb_rows = NB_ROWS
        self.nb_cols = NB_COLS
        self.grid: list[list[int]] = [
            [PIECE_CODES["empty"] for _ in range(self.nb_cols)] for _ in range(self.nb_rows)
        ]

    def clear(self):
        for r in range(self.nb_rows):
            for c in range(self.nb_cols):
                self.grid[r][c] = PIECE_CODES["empty"]

    def get(self, row: int, col: int) -> int:
        if 0 <= row < self.nb_rows and 0 <= col < self.nb_cols:
            return self.grid[row][col]
        return PIECE_CODES["empty"]

    def rotate_piece(self, color: PIECE_COLOR, rotation: int) -> tuple[tuple[int, int], ...]:
        if rotation not in (0, 90, 180, 270):
            raise ValueError("rotation must be 0, 90, 180, or 270")
        base = PIECE_DIMENSIONS[color]
        rotated: list[tuple[int, int]] = []
        for r, c in base:
            if rotation == 0:
                nr, nc = r, c
            elif rotation == 90:
                nr, nc = c, -r
            elif rotation == 180:
                nr, nc = -r, -c
            else:  # 270
                nr, nc = -c, r
            rotated.append((nr, nc))
        min_r = min(pt[0] for pt in rotated)
        min_c = min(pt[1] for pt in rotated)
        normalized = tuple((r - min_r, c - min_c) for r, c in rotated)
        return normalized

    def can_place_piece(self, color: PIECE_COLOR, origin_row: int, origin_col: int, rotation: int = 0) -> bool:
        if color not in PIECE_DIMENSIONS or color == "empty":
            return False
        code = PIECE_CODES[color]
        try:
            offsets = self.rotate_piece(color, rotation)
        except ValueError:
            return False
        for dr, dc in offsets:
            r = origin_row + dr
            c = origin_col + dc
            if not (0 <= r < self.nb_rows and 0 <= c < self.nb_cols):
                return False
            cell = self.grid[r][c]
            if cell not in (PIECE_CODES["empty"], code):
                return False
        return True

    def place_piece(self, color: PIECE_COLOR, origin_row: int, origin_col: int, rotation: int = 0) -> bool:
        if not self.can_place_piece(color, origin_row, origin_col, rotation):
            return False
        code = PIECE_CODES[color]
        offsets = self.rotate_piece(color, rotation)
        for dr, dc in offsets:
            r = origin_row + dr
            c = origin_col + dc
            self.grid[r][c] = code
        return True

    def remove_piece(self, color: PIECE_COLOR):
        code = PIECE_CODES.get(color)
        if code is None:
            return
        for r in range(self.nb_rows):
            for c in range(self.nb_cols):
                if self.grid[r][c] == code:
                    self.grid[r][c] = PIECE_CODES["empty"]

    def generate_puzzle(self):
        # Placeholder for puzzle generation logic
        pass