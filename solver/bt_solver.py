"""Backtracking solver scaffolding for the IQ Puzzler board."""
from __future__ import annotations

import copy
from typing import Dict, Iterable, List, Sequence, Tuple

from game_logic.board import Board
from game_logic import PIECE_COLOR, PIECE_DIMENSIONS

Placement = Tuple[int, int, int, bool, bool]


class BTSolver:
    """Generate-and-test solver following the CSP template.

    V (variables) == remaining piece colors to place.
    A (assignment) == mapping piece -> placement tuple.
    """

    def __init__(self, board: Board):
        self.board = board
        self.variables: List[PIECE_COLOR] = []
        self.assignment: Dict[PIECE_COLOR, Placement] = {}
        self.piece: PIECE_COLOR | None = None
        self._piece_sizes = {color: len(shape) for color, shape in PIECE_DIMENSIONS.items()}
        self.solution_steps: List[tuple[PIECE_COLOR, Placement]] = []
        self.nodes_visited = 0
        self.placements_tested = 0

    def solve(self) -> bool:
        """Return True when a complete tiling is found; False otherwise."""
        original_board = self.board
        working_board = copy.deepcopy(original_board)
        self.board = working_board
        self.variables = self._ordered_variables()
        self.assignment.clear()
        self.solution_steps.clear()
        self.nodes_visited = 0
        self.placements_tested = 0
        try:
            return self._backtrack(self.variables, self.assignment, [])
        finally:
            self.board = original_board

    def _backtrack(
        self,
        remaining: Sequence[PIECE_COLOR],
        assignment: Dict[PIECE_COLOR, Placement],
        path: List[tuple[PIECE_COLOR, Placement]],
    ) -> bool:
        self.nodes_visited += 1
        if not remaining:
            self.solution_steps = list(path)
            return True
        piece = self._select_variable(remaining)
        for placement in self._domain_for(piece):
            self.placements_tested += 1
            if self._consistent(piece, placement):
                self._commit(piece, placement)
                assignment[piece] = placement

                next_vars: List[PIECE_COLOR] = [p for p in remaining if p != piece]
                path.append((piece, placement))
                if self._backtrack(next_vars, assignment, path):
                    return True
                path.pop()
                assignment.pop(piece, None)
                self._undo(piece)
        return False

    def _ordered_variables(self) -> List[PIECE_COLOR]:
        return sorted(
            self.board.available,
            key=lambda color: (-self._piece_sizes.get(color, 0), color),
        )

    def _select_variable(self, variables: Sequence[PIECE_COLOR]) -> PIECE_COLOR:
        best_piece = variables[0]
        best_count: int | None = None
        for piece in variables:
            placements = list(self._domain_for(piece))
            count = len(placements)
            if count == 0:
                return piece
            if best_count is None or count < best_count:
                best_piece = piece
                best_count = count
        return best_piece

    def _domain_for(self, piece: PIECE_COLOR) -> Iterable[Placement]:
        placements: List[Placement] = []
        seen_orientations: set[tuple[tuple[int, int], ...]] = set()
        for rotation in (0, 90, 180, 270):
            for flip_h in (False, True):
                for flip_v in (False, True):
                    try:
                        offsets = self.board.transform_piece(piece, rotation, flip_h, flip_v)
                    except ValueError:
                        continue
                    if offsets in seen_orientations:
                        continue
                    seen_orientations.add(offsets)
                    for row in range(self.board.nb_rows):
                        for col in range(self.board.nb_cols):
                            if self.board.can_place_piece(piece, row, col, rotation, flip_h, flip_v):
                                placements.append((row, col, rotation, flip_h, flip_v))
        return placements

    def _consistent(self, piece: PIECE_COLOR, placement: Placement) -> bool:
        if piece not in self.board.available:
            return False
        row, col, rotation, flip_h, flip_v = placement
        if not self.board.can_place_piece(piece, row, col, rotation, flip_h, flip_v):
            return False
        # Speculatively place the piece to evaluate downstream constraints.
        self.board.place_piece(piece, row, col, rotation, flip_h, flip_v)
        valid = self.board.initial_layout_valid() and self._check_connectivity()
        self.board.undo_last_piece()
        return valid

    def _commit(self, piece: PIECE_COLOR, placement: Placement) -> None:
        row, col, rotation, flip_h, flip_v = placement
        self.board.place_piece(piece, row, col, rotation, flip_h, flip_v)
        if piece in self.board.available:
            self.board.available.remove(piece)

    def _undo(self, piece: PIECE_COLOR) -> None:
        self.board.undo_last_piece()
        if piece not in self.board.available:
            self.board.available.append(piece)

    def reset(self) -> None:
        """Reset board state before starting a new solve attempt."""
        self.board.clear()
        self.variables.clear()
        self.assignment.clear()

    def _check_connectivity(self) -> bool:
        regions = self.board.empty_regions()
        if not regions:
            return True
        remaining_sizes = [self._piece_sizes.get(color, 0) for color in self.board.available if color != "empty"]
        if not remaining_sizes:
            return False
        min_size = min(size for size in remaining_sizes if size > 0)
        if any(len(region) < min_size for region in regions):
            return False
        for region in regions:
            capacity = len(region)
            if all(size > capacity for size in remaining_sizes):
                return False
        return True
