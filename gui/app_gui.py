import tkinter as tk
from game_logic.board import Board
from gui.main_menu import MainMenu
from gui.game_view import GameView

class AppGUI:
    """Container/manager for all application views (menus & game screens)."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("IQ Puzzler AI Solver")
        self.root.geometry("1080x720")
        self.board = Board()

        self._container = tk.Frame(root)
        self._container.pack(fill="both", expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)

        self.frames: dict[str, tk.Frame] = {}
        self.show_menu()
        self.show("MainMenu")

    def show_menu(self):
        frame = MainMenu(self._container, self)
        self.frames["MainMenu"] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def show(self, name: str):
        frame = self.frames[name]
        frame.tkraise()

    def back_to_menu(self):
        self.show("MainMenu")

    def start_game(self, mode: str):
        """Create or recreate a GameView with the given mode ('human'|'auto')."""
        old = self.frames.get("GameView")
        if old is not None:
            old.destroy()
        gv = GameView(self._container, self, mode=mode)
        self.frames["GameView"] = gv
        gv.grid(row=0, column=0, sticky="nsew")
        self.show("GameView")
