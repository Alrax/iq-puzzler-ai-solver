import random
from typing import List, Tuple
from game_logic.constants import *

class Board:
    """Board backed by a 2D list of ints (piece codes). 0 = empty.

    Supports rotation (0,90,180,270 clockwise) and optional horizontal / vertical flips.
    Placement signature:
        place_piece(color, origin_row, origin_col, rotation=0, flip_h=False, flip_v=False)
    """

    def __init__(self):
        self.nb_rows = NB_ROWS
        self.nb_cols = NB_COLS
        self.grid: list[list[int]] = [
            [PIECE_CODES["empty"] for _ in range(self.nb_cols)] for _ in range(self.nb_rows)
        ]
        self.available = [c for c in PIECE_COLOR.__args__ if c != "empty"]
        self.history: List[Tuple[PIECE_COLOR, List[Tuple[int, int]]]] = []
        # Automatically generate initial puzzle layout
        self.generate_puzzle()

    def clear(self):
        for r in range(self.nb_rows):
            for c in range(self.nb_cols):
                self.grid[r][c] = PIECE_CODES["empty"]
        self.available = [c for c in PIECE_COLOR.__args__ if c != "empty"]
        self.history.clear()

    def get(self, row: int, col: int) -> int:
        if 0 <= row < self.nb_rows and 0 <= col < self.nb_cols:
            return self.grid[row][col]
        return PIECE_CODES["empty"]

    def transform_piece(self, color: PIECE_COLOR, rotation: int = 0, flip_h: bool = False, flip_v: bool = False) -> tuple[tuple[int, int], ...]:
        if rotation not in (0, 90, 180, 270):
            raise ValueError("rotation must be 0, 90, 180, or 270")
        base = PIECE_DIMENSIONS[color]
        transformed: list[tuple[int, int]] = []
        for r, c in base:
            if flip_h:
                c = -c
            if flip_v:
                r = -r
            if rotation == 0:
                nr, nc = r, c
            elif rotation == 90:
                nr, nc = c, -r
            elif rotation == 180:
                nr, nc = -r, -c
            else:  # 270
                nr, nc = -c, r
            transformed.append((nr, nc))
        min_r = min(pt[0] for pt in transformed)
        min_c = min(pt[1] for pt in transformed)
        normalized = tuple((r - min_r, c - min_c) for r, c in transformed)
        return normalized

    def can_place_piece(self, color: PIECE_COLOR, origin_row: int, origin_col: int,
                        rotation: int = 0, flip_h: bool = False, flip_v: bool = False) -> bool:
        if color not in self.available or color == "empty":
            return False
        code = PIECE_CODES[color]
        try:
            offsets = self.transform_piece(color, rotation, flip_h, flip_v)
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

    def place_piece(self, color: PIECE_COLOR, origin_row: int, origin_col: int,
                    rotation: int = 0, flip_h: bool = False, flip_v: bool = False) -> bool:
        if not self.can_place_piece(color, origin_row, origin_col, rotation, flip_h, flip_v):
            return False
        code = PIECE_CODES[color]
        offsets = self.transform_piece(color, rotation, flip_h, flip_v)
        cells: List[Tuple[int, int]] = []
        for dr, dc in offsets:
            r = origin_row + dr
            c = origin_col + dc
            self.grid[r][c] = code
            cells.append((r, c))
        self.history.append((color, cells))
        return True

    def remove_piece(self, color: PIECE_COLOR):
        code = PIECE_CODES.get(color)
        if code is None:
            return
        for r in range(self.nb_rows):
            for c in range(self.nb_cols):
                if self.grid[r][c] == code:
                    self.grid[r][c] = PIECE_CODES["empty"]

    def undo_last_piece(self) -> PIECE_COLOR | None:
        if not self.history:
            return None
        color, _cells = self.history.pop()
        code = PIECE_CODES[color]
        for r in range(self.nb_rows):
            for c in range(self.nb_cols):
                if self.grid[r][c] == code:
                    self.grid[r][c] = PIECE_CODES["empty"]
        if color not in self.available:
            self.available.append(color)
        return color

    def empty_regions(self) -> list[set[tuple[int,int]]]:
        """Return list of connected empty regions (4-direction)."""
        visited = set()
        regions = []
        for r in range(self.nb_rows):
            for c in range(self.nb_cols):
                if self.grid[r][c] != PIECE_CODES["empty"] or (r, c) in visited:
                    continue
                stack = [(r, c)]
                comp = set()
                while stack:
                    cr, cc = stack.pop()
                    if (cr, cc) in visited:
                        continue
                    visited.add((cr, cc))
                    comp.add((cr, cc))
                    for nr, nc in ((cr-1, cc), (cr+1, cc), (cr, cc-1), (cr, cc+1)):
                        if 0 <= nr < self.nb_rows and 0 <= nc < self.nb_cols:
                            if self.grid[nr][nc] == PIECE_CODES["empty"] and (nr, nc) not in visited:
                                stack.append((nr, nc))
                regions.append(comp)
        return regions

    def initial_layout_valid(self) -> bool:
        """No isolated empty region smaller than smallest piece size."""
        regions = self.empty_regions()
        for comp in regions:
            if len(comp) < 3:
                return False
        if "light_blue" not in self.available:
            for comp in regions:
                if len(comp) < 4:
                    return False
        return True

    def generate_puzzle(self, max_total_attempts: int = 100, piece_attempts: int = 200) -> None:
        """Generate initial puzzle by placing two random distinct pieces."""
        for _ in range(max_total_attempts):
            # Reset board each global attempt
            self.clear()
            chosen = random.sample(self.available, 2)
            success = True
            for color in chosen:
                placed = False
                for _ in range(piece_attempts):
                    rotation = random.choice([0, 90, 180, 270])
                    flip_h = random.choice([False, True])
                    flip_v = random.choice([False, True])
                    origin_row = random.randint(0, self.nb_rows - 1)
                    origin_col = random.randint(0, self.nb_cols - 1)
                    if self.can_place_piece(color, origin_row, origin_col, rotation, flip_h, flip_v):
                        self.place_piece(color, origin_row, origin_col, rotation, flip_h, flip_v)
                        placed = True
                        self.available.remove(color)
                        break
                if not placed:
                    success = False
                    break
            if not success:
                continue
            if self.initial_layout_valid():
                self.history.clear()
                return  # successful generation
        self.clear()

    # Debug helper
    def __str__(self) -> str:
        """Return a readable string of the board grid.
        Empty cells shown as '.', others as their numeric code.
        """
        lines: list[str] = []
        for r in range(self.nb_rows):
            row_str = []
            for c in range(self.nb_cols):
                val = self.grid[r][c]
                row_str.append('.' if val == PIECE_CODES["empty"] else str(val))
            lines.append(' '.join(row_str))
        return '\n'.join(lines)

    def debug_print(self):
        """Print the board to stdout for quick debugging."""
        print(self.__str__())