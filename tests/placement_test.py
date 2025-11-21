import unittest

from game_logic import Board, PIECE_CODES, PIECE_DIMENSIONS, PIECE_COLOR


def reset_board(board: Board):
	"""Ensure board is empty and all pieces are available for tests."""
	board.clear()
	board.available = [c for c in PIECE_COLOR.__args__ if c != "empty"]


class TestPiecePlacement(unittest.TestCase):
	def setUp(self):
		# Board generates a puzzle on init; ensure clean state for each test.
		self.board = Board()
		reset_board(self.board)

	def test_place_piece_all_rotations_and_flips_center(self):
		color = "yellow"
		origin_row, origin_col = 0, 0
		for rotation in (0, 90, 180, 270):
			for flip_h in (False, True):
				for flip_v in (False, True):
					reset_board(self.board)
					placed = self.board.place_piece(color, origin_row, origin_col, rotation, flip_h, flip_v)
					self.assertTrue(placed, f"Failed to place {color} with rot={rotation} flip_h={flip_h} flip_v={flip_v}")
					# Verify cells contain the piece code
					code = PIECE_CODES[color]
					offsets = self.board.transform_piece(color, rotation, flip_h, flip_v)
					for dr, dc in offsets:
						self.assertEqual(self.board.get(origin_row + dr, origin_col + dc), code)

	def test_cannot_place_out_of_bounds(self):
		color = "yellow"
		# Try position near right edge where rotation should push piece out.
		origin_row = 0
		origin_col = self.board.nb_cols - 1
		can_place = self.board.can_place_piece(color, origin_row, origin_col, rotation=0)
		self.assertFalse(can_place, "Should not place piece partially outside right edge")

	def test_overlap_different_colors_fails(self):
		# Place a piece then attempt overlapping with different color.
		self.assertTrue(self.board.place_piece("yellow", 0, 0, rotation=0))
		# Attempt to place orange overlapping some yellow cells
		overlap_can = self.board.can_place_piece("orange", 0, 0, rotation=0)
		self.assertFalse(overlap_can, "Should not allow overlapping different colored pieces")

	def test_transform_normalization_non_negative(self):
		color = "purple"
		for rotation in (0, 90, 180, 270):
			for flip_h in (False, True):
				for flip_v in (False, True):
					offsets = self.board.transform_piece(color, rotation, flip_h, flip_v)
					self.assertTrue(all(r >= 0 and c >= 0 for r, c in offsets), "Offsets not normalized to non-negative")
					self.assertEqual(len(offsets), len(PIECE_DIMENSIONS[color]))

	def test_invalid_rotation_rejected(self):
		with self.assertRaises(ValueError):
			self.board.transform_piece("yellow", rotation=45)
		# can_place should return False rather than raise.
		self.assertFalse(self.board.can_place_piece("yellow", 0, 0, rotation=45))


if __name__ == "__main__":
	unittest.main()
