import tkinter as tk

def make_primary_button(parent, text: str, command, font, **overrides) -> tk.Button:
    style = {
        "bg": "#2d2d2d",
        "fg": "#f0f0f0",
        "activebackground": "#333333",
        "activeforeground": "#f0f0f0",
        "relief": tk.FLAT,
        "cursor": "hand2",
        "padx": 24,
        "pady": 18,
        "font": font,
    }
    style.update(overrides)
    return tk.Button(parent, text=text, command=command, **style)
