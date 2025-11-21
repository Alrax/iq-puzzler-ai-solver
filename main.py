import tkinter as tk
from board import Board
from puzzler_gui import PuzzlerGUI

def main():
    root = tk.Tk() # Create a new window
    for i in range(100):
        board = Board()  # Initialize a new board each iteration
        print(f"Board #{i+1}")
        board.debug_print()  # Print/debug the board

if __name__ == "__main__":
    main()