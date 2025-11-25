import tkinter as tk
from gui.components.styled_button import make_primary_button

class MainMenu(tk.Frame):
    BG_COLOR = "#121212"
    FG_COLOR = "#f0f0f0"

    def __init__(self, parent, app):
        super().__init__(parent, bg=self.BG_COLOR)
        self.app = app
        self.title_font = ("Segoe UI", 32, "bold")
        self.button_font = ("Segoe UI", 16, "bold")
        self.setup_layout()

    def setup_layout(self):
        # Use grid for scalable placement
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=2)
        
        # Logo / title area
        self.top_frame = tk.Frame(self, bg=self.BG_COLOR)
        self.top_frame.grid(row=0, column=0, sticky="nsew")
        path = "gui/assets/iq_puzzler_logo.png"
        try:
            logo_img = tk.PhotoImage(file=path)
            tk.Label(self.top_frame, image=logo_img, bg=self.BG_COLOR).pack(expand=True)
            # Keep reference to avoid GC
            self.logo_img = logo_img
        except Exception:
            tk.Label(self.top_frame, text="IQ Puzzler AI Solver", fg=self.FG_COLOR, bg=self.BG_COLOR, font=self.title_font).pack(expand=True)
        
        # Buttons area
        self.bottom_frame = tk.Frame(self, bg=self.BG_COLOR)
        self.bottom_frame.grid(row=1, column=0, sticky="nsew")
        self.bottom_frame.columnconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(1, weight=1)
        self.manual_btn = make_primary_button(
            self.bottom_frame,
            text="Play Manual Game",
            command=lambda: self.app.start_game("human"),
            font=self.button_font,
        )
        self.auto_btn = make_primary_button(
            self.bottom_frame,
            text="Start Auto Solver",
            command=lambda: self.app.start_game("auto"),
            font=self.button_font,
        )
        self.manual_btn.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.auto_btn.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
