import tkinter as tk
from board import Board
from puzzler_gui import PuzzlerGUI

def main():
    root = tk.Tk() # Create a new window
    game_display = PuzzlerGUI(root) # Create a new display
    root.mainloop() # Start the main loop

if __name__ == "__main__":
    main()