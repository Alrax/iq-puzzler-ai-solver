import tkinter as tk
from game_logic.board import Board
from gui.puzzler_gui import PuzzlerGUI

def main():
    root = tk.Tk() # Create a new window
    board = Board()  # Initialize a new board
    board.debug_print()
    print("Place a piece on the board:")
    board.place_piece("red", 0, 0, rotation=0, flip_h=False, flip_v=False)
    board.debug_print()

if __name__ == "__main__":
    main()