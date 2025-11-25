import tkinter as tk
import random
from typing import cast
from gui.components.styled_button import make_primary_button
from game_logic.constants import PIECE_CODES, PIECE_COLOR
from game_logic.board import Board

class GameView(tk.Frame):
    BG_COLOR = "#121212"
    FG_COLOR = "#f0f0f0"
    PIECE_HOVER_COLOR = "#a12525"

    COLOR_PALETTE = {
        "yellow": "#f8e71c",
        "orange": "#f5a623",
        "red": "#d0021b",
        "burgundy": "#7b1e3a",
        "pink": "#ff6fae",
        "purple": "#9013fe",
        "dark_blue": "#003f7f",
        "blue": "#4a90e2",
        "light_blue": "#8dd3ff",
        "turquoise": "#1abc9c",
        "lime": "#b8e986",
        "green": "#417505",
        "empty": "#292929",
    }

    def __init__(self, parent, app, mode: str = "human"):
        super().__init__(parent, bg=self.BG_COLOR)
        self.app = app
        self.mode = mode  # 'human' or 'auto'
        self.board: Board = app.board
        self.title_font = ("Segoe UI", 24, "bold")
        self.body_font = ("Segoe UI", 14)
        self.small_font = ("Segoe UI", 12)
        self._piece_preview_side = 160
        self._piece_preview_ratio = 2/3

        # First available piece
        self.selected_piece: PIECE_COLOR | None = None
        self.selected_piece =  self.board.available[0] if self.board.available else None
        self.rotation = 0
        self.flip_h = False
        self.flip_v = False

        # Widgets containers
        self.board_cells: list[list[tk.Label]] = []
        self.piece_frame: tk.Frame | None = None
        self._reverse_codes = {v: k for k, v in PIECE_CODES.items()}
        self.build_layout()
        self.render_piece_preview()
        self.refresh_board()

    def build_layout(self):
        # Layout: three rows (title, board, available pieces)
        self.columnconfigure(0, weight=3, uniform="layout")
        self.columnconfigure(1, weight=1, uniform="layout")
        self.rowconfigure(0, weight=1)  # 1/8
        self.rowconfigure(1, weight=5)  # 5/8
        self.rowconfigure(2, weight=2)  # 2/8

        # Header
        header = tk.Frame(self, bg=self.BG_COLOR)
        header.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=20, pady=(10, 5))
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=1)
        header.columnconfigure(2, weight=1)
        home_btn = make_primary_button(
            header,
            text="🏠 Home",
            command=self.app.back_to_menu,
            font=self.small_font,
            padx=16,
            pady=10,
        )
        home_btn.grid(row=0, column=0, sticky="w")
        title_txt = "Manual Play" if self.mode == "human" else "Auto Solver"
        title = tk.Label(header, text=title_txt, fg=self.FG_COLOR, bg=self.BG_COLOR, font=self.title_font)
        title.grid(row=0, column=1, sticky="n")

        # Board area to center vertically and scale from width
        self.board_area = tk.Frame(self, bg=self.BG_COLOR)
        self.board_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10,5))
        self.board_area.grid_rowconfigure(0, weight=1)
        self.board_area.grid_rowconfigure(2, weight=1)
        self.board_area.grid_columnconfigure(0, weight=1)

        self.board_frame = tk.Frame(self.board_area, bg=self.BG_COLOR)
        self.board_frame.grid(row=1, column=0)
        self.board_cells = []
        initial_size = 30
        for r in range(self.board.nb_rows):
            row_cells = []
            for c in range(self.board.nb_cols):
                cell = tk.Frame(self.board_frame, bg="#1e1e1e", width=initial_size, height=initial_size, relief=tk.RAISED, bd=1)
                cell.grid(row=r, column=c, padx=1, pady=1)
                cell.grid_propagate(False)
                cell.bind("<Button-1>", lambda _e, row=r, col=c: self.handle_board_click(row, col))
                row_cells.append(cell)
            self.board_cells.append(row_cells)
        self.board_area.bind("<Configure>", lambda _e: self.resize_board_cells())

        # Sidebar
        sidebar = tk.Frame(self, bg=self.BG_COLOR)
        sidebar.grid(row=1, column=1, sticky="nsew", padx=10, pady=10,)

        # Sidebar internal: top section ~2/8, bottom section remainder
        sidebar.rowconfigure(0, weight=2)
        sidebar.rowconfigure(1, weight=6)
        sidebar.columnconfigure(0, weight=1)

        # Sidebar top: Selected piece + rotate/flip controls
        sidebar_top = tk.Frame(sidebar, bg=self.BG_COLOR)
        sidebar_top.grid(row=0, column=0, sticky="new")
        piece_label_text = "Selected Piece"
        tk.Label(sidebar_top, text=piece_label_text, fg=self.FG_COLOR, bg=self.BG_COLOR, font=self.body_font).pack(anchor="w")

        # Keep piece preview within fixed min size but allow width scaling with window
        self.piece_frame = tk.Frame(sidebar_top, bg=self.BG_COLOR, height=self._piece_preview_side)
        self.piece_frame.pack(fill="x", pady=4)
        self.piece_frame.pack_propagate(False)
        self.piece_frame.bind("<Configure>", self._handle_piece_frame_resize)

        controls = tk.Frame(sidebar_top, bg=self.BG_COLOR)
        controls.pack(fill="x", pady=(6,0))
        for i in range(3):
            controls.columnconfigure(i, weight=1, uniform="controls")
        button_kwargs = {
            "font": self.small_font,
            "padx": 12,
            "pady": 8,
        }
        self.rotate_btn = make_primary_button(controls, text="Rotate (0°)", command=self.rotate_piece, **button_kwargs)
        self.rotate_btn.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
        self.flip_v_btn = make_primary_button(controls, text="Flip V (Off)", command=self.flip_piece_v, **button_kwargs)
        self.flip_v_btn.grid(row=0, column=1, padx=4, pady=4, sticky="nsew")
        self.flip_h_btn = make_primary_button(controls, text="Flip H (Off)", command=self.flip_piece_h, **button_kwargs)
        self.flip_h_btn.grid(row=0, column=2, padx=4, pady=4, sticky="nsew")

        # Sidebar bottom: actions
        sidebar_bottom = tk.Frame(sidebar, bg=self.BG_COLOR)
        sidebar_bottom.grid(row=1, column=0, sticky="sew")
        for i in range(3):
            sidebar_bottom.columnconfigure(i, weight=1, uniform="actions")
        take_back_btn = make_primary_button(
            sidebar_bottom,
            text="Take Back Piece",
            command=self.take_back_piece,
            font=self.small_font,
            padx=12,
            pady=8,
        )
        take_back_btn.grid(row=0, column=0, padx=4, pady=6, sticky="nsew")
        if self.mode == "auto":
            solve_btn = make_primary_button(
                sidebar_bottom,
                text="Solve",
                command=lambda: None,
                font=self.small_font,
                padx=12,
                pady=8,
            )
            solve_btn.grid(row=0, column=1, padx=4, pady=6, sticky="nsew")
        else:
            spacer = tk.Frame(sidebar_bottom, bg=self.BG_COLOR)
            spacer.grid(row=0, column=1, sticky="nsew")
        filler = tk.Frame(sidebar_bottom, bg=self.BG_COLOR)
        filler.grid(row=0, column=2, sticky="nsew")

        # Selection row
        self.selection_frame = tk.Frame(self, bg=self.BG_COLOR)
        self.selection_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(5,10))
        self.selection_frame.columnconfigure(0, weight=1)
        sel_label = tk.Label(self.selection_frame, text="Pieces Left:", fg=self.FG_COLOR, bg=self.BG_COLOR, font=self.small_font)
        sel_label.grid(row=0, column=0, sticky="w", pady=(0,6))
        self.pieces_container = tk.Frame(self.selection_frame, bg=self.BG_COLOR, height=120)
        self.pieces_container.grid(row=1, column=0, sticky="ew")
        self.pieces_container.columnconfigure(0, weight=1)
        self.pieces_container.pack_propagate(False)
        self.pieces_container.bind("<Configure>", lambda _e: self.render_available_pieces())
        self.render_available_pieces()

    def rotate_piece(self):
        self.rotation = (self.rotation + 90) % 360
        self.render_piece_preview()

    def flip_piece_v(self):
        self.flip_v = not self.flip_v
        self.render_piece_preview()
        self.refresh_control_labels()

    def flip_piece_h(self):
        self.flip_h = not self.flip_h
        self.render_piece_preview()
        self.refresh_control_labels()

    def color_for_code(self, code: int) -> str:
        name = self._reverse_codes.get(code, "empty")
        return self.COLOR_PALETTE.get(name, "#444444")

    def refresh_board(self):
        for r in range(self.board.nb_rows):
            for c in range(self.board.nb_cols):
                code = self.board.grid[r][c]
                cell = self.board_cells[r][c]
                cell.configure(bg=self.color_for_code(code))

    def render_piece_preview(self):
        if self.piece_frame is None:
            return
        for child in list(self.piece_frame.winfo_children()):
            child.destroy()
        if self.selected_piece is None:
            tk.Label(self.piece_frame, text="None", fg=self.FG_COLOR, bg=self.BG_COLOR, font=self.small_font).pack()
            return
        offsets = self.board.transform_piece(self.selected_piece, self.rotation, self.flip_h, self.flip_v)
        max_r = max(r for r,_ in offsets)
        max_c = max(c for _,c in offsets)
        # Determine cell size based on available width/height
        self.piece_frame.update_idletasks()
        square_side = max(min(self.piece_frame.winfo_width(), self.piece_frame.winfo_height()) - 10, 50)
        if square_side <= 0:
            square_side = 50
        dimension = max(max_r + 1, max_c + 1)
        cell_size = max(12, square_side // dimension)

        grid = tk.Frame(self.piece_frame, bg=self.BG_COLOR)
        grid.pack()
        for r in range(max_r+1):
            for c in range(max_c+1):
                holder = tk.Frame(grid, width=cell_size, height=cell_size, bg=self.BG_COLOR)
                holder.grid(row=r, column=c, padx=1, pady=1)
                holder.grid_propagate(False)
        piece_color = self.COLOR_PALETTE[self.selected_piece]
        for r,c in offsets:
            cell = tk.Frame(grid, width=cell_size, height=cell_size, bg=piece_color, relief=tk.FLAT, bd=0)
            cell.grid(row=r, column=c, padx=1, pady=1)
            cell.grid_propagate(False)


    def _handle_piece_frame_resize(self, _event):
        if self.piece_frame is None:
            return
        width = self.piece_frame.winfo_width()
        target_side = int(width * self._piece_preview_ratio)
        if target_side <= 0:
            return
        if target_side == self._piece_preview_side:
            return
        self._piece_preview_side = target_side
        self.piece_frame.configure(height=target_side)
        self.after_idle(self.render_piece_preview)

    def refresh_control_labels(self):
        # Update control button texts to show current rotation/flip state
        if hasattr(self, 'rotate_btn'):
            self.rotate_btn.configure(text=f"Rotate ({self.rotation}°)")
        if hasattr(self, 'flip_v_btn'):
            self.flip_v_btn.configure(text=f"Flip V ({'On' if self.flip_v else 'Off'})")
        if hasattr(self, 'flip_h_btn'):
            self.flip_h_btn.configure(text=f"Flip H ({'On' if self.flip_h else 'Off'})")

    def resize_board_cells(self):
        # Determine new cell size based on available board_area width so board follows window width
        self.board_area.update_idletasks()
        avail_w = max(self.board_area.winfo_width() - 40, 50)
        avail_h = max(self.board_area.winfo_height() - 40, 50)
        cols = self.board.nb_cols
        rows = self.board.nb_rows
        cell_w = avail_w // cols
        cell_h = avail_h // rows
        cell_size = max(12, min(cell_w, cell_h))
        for r in range(rows):
            for c in range(cols):
                cell = self.board_cells[r][c]
                cell.configure(width=cell_size, height=cell_size)
        # Reapply colors
        self.refresh_board()

    # --- Piece selection row ---
    def render_available_pieces(self):
        if self.pieces_container is None:
            return
        for child in list(self.pieces_container.winfo_children()):
            child.destroy()
        avail = [c for c in self.board.available if c != "empty"]
        if not avail:
            tk.Label(self.pieces_container, text="None", fg=self.FG_COLOR, bg=self.BG_COLOR, font=self.small_font).pack(side=tk.LEFT)
            return
        # Compute mini cell size based on container height
        self.pieces_container.update_idletasks()
        container_h = max(self.pieces_container.winfo_height(), 50)
        # leave margin for padding; target rows <= max piece height (<=4)
        cell = max(8, (container_h - 10) // 4)
        for color in avail:
            mini = self.render_available_piece(color, cell)
            mini.pack(side=tk.LEFT, padx=4)

    def render_available_piece(self, color: PIECE_COLOR, cell_size: int) -> tk.Frame:
        frame = tk.Frame(self.pieces_container, bg=self.BG_COLOR, bd=0, padx=1, pady=1, highlightbackground=self.PIECE_HOVER_COLOR)
        offsets = self.board.transform_piece(color, 0, False, False)
        max_r = max(r for r,_ in offsets)
        max_c = max(c for _,c in offsets)
        grid = tk.Frame(frame, bg=self.BG_COLOR)
        grid.pack()
        for r in range(max_r+1):
            for c in range(max_c+1):
                holder = tk.Frame(grid, width=cell_size, height=cell_size, bg=self.BG_COLOR)
                holder.grid(row=r, column=c, padx=1, pady=1)
                holder.grid_propagate(False)
        piece_color = self.COLOR_PALETTE[color]
        for r,c in offsets:
            cell = tk.Frame(grid, width=cell_size, height=cell_size, bg=piece_color, relief=tk.FLAT, bd=0)
            cell.grid(row=r, column=c, padx=1, pady=1)
            cell.grid_propagate(False)
            cell.bind("<Button-1>", lambda _e, col=color: self.select_piece(col))
        frame.bind("<Button-1>", lambda _e, col=color: self.select_piece(col))
        
        return frame

    def select_piece(self, color: PIECE_COLOR):
        self.selected_piece = color
        self.rotation = 0
        self.flip_h = False
        self.flip_v = False
        self.render_piece_preview()
        self.refresh_control_labels()

    def handle_board_click(self, row: int, col: int):
        if self.selected_piece is None:
            return
        color = self.selected_piece
        if not self.board.can_place_piece(color, row, col, self.rotation, self.flip_h, self.flip_v):
            return
        placed = self.board.place_piece(color, row, col, self.rotation, self.flip_h, self.flip_v)
        if not placed:
            return
        try:
            self.board.available.remove(color)
        except ValueError:
            pass
        self.refresh_board()
        self.render_available_pieces()
        self._select_next_available_piece()

    def _select_next_available_piece(self):
        next_piece = None
        for color in self.board.available:
            if color == "empty":
                continue
            next_piece = cast(PIECE_COLOR, color)
            break
        self.selected_piece = next_piece
        self.rotation = 0
        self.flip_h = False
        self.flip_v = False
        self.render_piece_preview()
        self.refresh_control_labels()

    def take_back_piece(self):
        color = self.board.undo_last_piece()
        if color is None:
            return
        self.selected_piece = cast(PIECE_COLOR, color)
        self.rotation = 0
        self.flip_h = False
        self.flip_v = False
        self.refresh_board()
        self.render_available_pieces()
        self.render_piece_preview()
        self.refresh_control_labels()

