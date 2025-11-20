import tkinter as tk

class PuzzlerGUI:
    def __init__(self, master):
        self.master = master
        master.title("IQ Puzzler AI Solver")

        self.label = tk.Label(master, text="Welcome to the IQ Puzzler AI Solver!")
        self.label.pack()

        self.start_manual_button = tk.Button(master, text="Play Manual Game", command=self.start_manual_game)
        self.start_manual_button.pack()

        self.start_auto_button = tk.Button(master, text="Start Auto Solver", command=self.start_auto_solver)
        self.start_auto_button.pack()


    def start_manual_game(self):
        print("Starting manual game...")

    def start_auto_solver(self):
        print("Starting auto solver...")