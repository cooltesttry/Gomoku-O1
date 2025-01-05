import tkinter as tk
from tkinter import messagebox
import time
from multiprocessing import Pool, cpu_count
import random
import copy
import math
import threading
import queue  # Use a thread-safe queue to communicate between threads

# ---------------------------
# Global Constants
# ---------------------------

BOARD_SIZE = 15  # The board is 15 x 15
CELL_SIZE = 40   # Each cell is 40 pixels
BOARD_PADDING = 20  # Padding (in pixels) around the board drawing
STONE_RADIUS = 15   # Radius of the stone in pixels

INF = float('inf')

# Difficulty settings: 'simple', 'medium', 'hard'
# Each difficulty has a certain number of MCTS simulations and a time limit (in seconds)
DIFFICULTY_LEVELS = {
    'simple': {'simulations': 500, 'time_limit': 2},
    'medium': {'simulations': 1000, 'time_limit': 5},
    'hard': {'simulations': 3000, 'time_limit': 12},
}


class Gomoku:
    """
    This is the main Gomoku class which handles:
    - UI rendering (Tkinter)
    - Game logic (player moves, AI moves, checking win condition, etc.)
    - AI interaction (via MCTS)
    """
    # Multi-language dictionary for user interface text
    translations = {
        "zh": {
            "title": "五子棋",
            "reset_button": "重新开始",
            "undo_button": "悔棋",
            "difficulty_button": "难度选择",
            "difficulty_window_title": "选择AI难度",
            "difficulty_window_label": "请选择AI的难度级别：",
            "ok_button": "确定",
            "current_player_prefix": "当前玩家: ",
            "black_time_prefix": "黑棋当前步时间: ",
            "white_time_prefix": "白棋当前步时间: ",
            "choose_side_title": "选择棋子",
            "choose_side_message": "你想先手（黑子）吗？",
            "game_over_title": "游戏结束",
            "game_over_win": "你赢了！",
            "game_over_lose": "电脑赢了！",
            "no_undo_title": "提示",
            "no_undo_message": "没有可以悔棋的步骤。",
            "game_end_no_undo_message": "游戏已结束，无法悔棋。",
            "black_label": "黑棋",
            "white_label": "白棋",
            "difficulty_labels": {
                "simple": "简单",
                "medium": "中等",
                "hard": "困难",
            }
        },
        "en": {
            "title": "Gomoku",
            "reset_button": "Restart",
            "undo_button": "Undo",
            "difficulty_button": "Difficulty",
            "difficulty_window_title": "Select AI Difficulty",
            "difficulty_window_label": "Please select AI difficulty:",
            "ok_button": "OK",
            "current_player_prefix": "Current Player: ",
            "black_time_prefix": "Black Time: ",
            "white_time_prefix": "White Time: ",
            "choose_side_title": "Choose Side",
            "choose_side_message": "Do you want to play first (Black)?",
            "game_over_title": "Game Over",
            "game_over_win": "You win!",
            "game_over_lose": "Computer wins!",
            "no_undo_title": "Info",
            "no_undo_message": "No move to undo.",
            "game_end_no_undo_message": "Game is over, cannot undo.",
            "black_label": "Black",
            "white_label": "White",
            "difficulty_labels": {
                "simple": "Easy",
                "medium": "Medium",
                "hard": "Hard",
            }
        },
        "es": {
            "title": "Gomoku",
            "reset_button": "Reiniciar",
            "undo_button": "Deshacer",
            "difficulty_button": "Dificultad",
            "difficulty_window_title": "Seleccionar dificultad",
            "difficulty_window_label": "Seleccione el nivel de dificultad de la IA:",
            "ok_button": "OK",
            "current_player_prefix": "Jugador actual: ",
            "black_time_prefix": "Tiempo de Negro: ",
            "white_time_prefix": "Tiempo de Blanco: ",
            "choose_side_title": "Elegir Color",
            "choose_side_message": "¿Quieres jugar primero (Negro)?",
            "game_over_title": "Fin del juego",
            "game_over_win": "¡Has ganado!",
            "game_over_lose": "¡La computadora ha ganado!",
            "no_undo_title": "Información",
            "no_undo_message": "No hay movimientos para deshacer.",
            "game_end_no_undo_message": "El juego ha terminado, no se puede deshacer.",
            "black_label": "Negro",
            "white_label": "Blanco",
            "difficulty_labels": {
                "simple": "Fácil",
                "medium": "Medio",
                "hard": "Difícil",
            }
        },
        "fr": {
            "title": "Gomoku",
            "reset_button": "Recommencer",
            "undo_button": "Annuler",
            "difficulty_button": "Difficulté",
            "difficulty_window_title": "Choisir la difficulté",
            "difficulty_window_label": "Veuillez sélectionner la difficulté de l'IA :",
            "ok_button": "OK",
            "current_player_prefix": "Joueur actuel : ",
            "black_time_prefix": "Temps Noir : ",
            "white_time_prefix": "Temps Blanc : ",
            "choose_side_title": "Choisir la Couleur",
            "choose_side_message": "Voulez-vous jouer en premier (Noir) ?",
            "game_over_title": "Fin de la partie",
            "game_over_win": "Vous avez gagné !",
            "game_over_lose": "L'ordinateur a gagné !",
            "no_undo_title": "Info",
            "no_undo_message": "Aucun coup à annuler.",
            "game_end_no_undo_message": "La partie est terminée, impossible d'annuler.",
            "black_label": "Noir",
            "white_label": "Blanc",
            "difficulty_labels": {
                "simple": "Facile",
                "medium": "Moyen",
                "hard": "Difficile",
            }
        }
    }

    def __init__(self, root):
        """
        Constructor for the Gomoku class.
        Initializes the Tkinter window, game variables, and UI components.
        """
        self.root = root
        # Set default UI language to English
        self.current_language = "en"
        # Default difficulty is set to "medium"
        self.current_difficulty = "medium"

        # Set window title according to the current language
        self.root.title(self.t("title"))

        # Calculate total canvas size for the board
        self.canvas_size = CELL_SIZE * (BOARD_SIZE - 1) + 2 * BOARD_PADDING

        # Create the Tkinter Canvas for drawing the Gomoku board
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg='#E0C9A5')
        self.canvas.pack()

        # Bind a mouse click event on the board
        self.canvas.bind("<Button-1>", self.click_event)

        # Create a control frame to hold language selection and buttons
        self.control_frame = tk.Frame(root, bg="#F8F8F8")
        self.control_frame.pack(fill="x", side="bottom", padx=10, pady=10)

        # 1. Language selection area
        self.language_frame = tk.Frame(self.control_frame, bg="#F8F8F8")
        self.language_frame.pack(side="left")

        tk.Label(self.language_frame, text="Lang:", bg="#F8F8F8").pack(side="left", padx=(0, 5))

        # Use StringVar to track the selected language
        self.selected_language = tk.StringVar(value=self.current_language)
        # Supported languages: Chinese, English, Spanish, French
        languages = [("中文", "zh"), ("EN", "en"), ("ES", "es"), ("FR", "fr")]
        for text, code in languages:
            rb = tk.Radiobutton(
                self.language_frame,
                text=text,
                value=code,
                variable=self.selected_language,
                command=lambda c=code: self.set_language(c),
                bg="#F8F8F8",
                activebackground="#E0E0E0",
                selectcolor="#D0D0D0"
            )
            rb.pack(side="left", padx=5)

        # 2. Buttons area: Restart, Undo, Difficulty
        self.button_frame = tk.Frame(self.control_frame, bg="#F8F8F8")
        self.button_frame.pack(side="right")

        # "Restart" button
        self.reset_button = tk.Button(
            self.button_frame,
            text=self.t("reset_button"),
            command=self.reset_game,
            bg="#ECECEC",
            activebackground="#D0D0D0",
            relief="groove"
        )
        self.reset_button.pack(side="left", padx=5)

        # "Undo" button
        self.undo_button = tk.Button(
            self.button_frame,
            text=self.t("undo_button"),
            command=self.undo_move,
            bg="#ECECEC",
            activebackground="#D0D0D0",
            relief="groove"
        )
        self.undo_button.pack(side="left", padx=5)

        # Difficulty selection button
        self.difficulty_button = tk.Button(
            self.button_frame,
            text=self.get_difficulty_button_text(),
            command=self.select_difficulty,
            bg="#ECECEC",
            activebackground="#D0D0D0",
            relief="groove"
        )
        self.difficulty_button.pack(side="left", padx=5)

        # Create a status frame to show labels (current player, timers, etc.)
        self.status_frame = tk.Frame(root)
        self.status_frame.pack(pady=10)

        # Show the current player's label (e.g., "Current Player: Black")
        self.current_player_label = tk.Label(
            self.status_frame,
            text=f"{self.t('current_player_prefix')}{self.t('black_label')}",
            font=("Arial", 12)
        )
        self.current_player_label.grid(row=0, column=0, padx=10)

        # Player's timer (when player is black)
        self.player_timer_label = tk.Label(
            self.status_frame,
            text=f"{self.t('black_time_prefix')}00.00",
            font=("Arial", 12)
        )
        self.player_timer_label.grid(row=0, column=1, padx=10)

        # AI's timer (when AI is white)
        self.ai_timer_label = tk.Label(
            self.status_frame,
            text=f"{self.t('white_time_prefix')}00.00",
            font=("Arial", 12)
        )
        self.ai_timer_label.grid(row=0, column=2, padx=10)

        # For measuring the time used by the player or the AI
        self.player_start_time = None
        self.ai_start_time = None

        # Initialize the board as a 15x15 2D list, each cell can be 'black', 'white', or ''
        self.board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # game_over indicates if the game has ended
        self.game_over = False
        # current_turn stores whose turn it is: 'black' or 'white'
        self.current_turn = 'black'
        # move_history is used for the "Undo" feature
        self.move_history = []
        # highlight is used to highlight the last move
        self.highlight = None

        # Thread-safe queue to receive AI moves from a background thread
        self.ai_move_queue = queue.Queue()

        # Set a timer in the main thread to process any incoming AI moves from the queue
        self.root.after(100, self.process_ai_move)

        # Draw the initial empty board (grid lines, star points, etc.)
        self.draw_board()

        # Set default difficulty parameters (MCTS simulations, time limit)
        self.set_default_difficulty()

        # Center the main window on screen
        self.center_main_window()

        # Prompt the user to choose whether to play black or white
        self.choose_side()

    def t(self, key):
        """
        Return the text in the currently selected language for the given key.
        If the key is not found, return the key itself.
        """
        return self.translations[self.current_language].get(key, key)

    def get_difficulty_button_text(self):
        """
        Return the label text for the difficulty selection button.
        For example: "Difficulty (Easy)" or "难度选择 (简单)"
        """
        diff_label = self.translations[self.current_language]["difficulty_labels"][self.current_difficulty]
        return f"{self.t('difficulty_button')} ({diff_label})"

    def set_language(self, lang_code):
        """
        Switch the current UI language to `lang_code`, and update all UI text immediately.
        """
        self.current_language = lang_code
        self.update_ui_text()

    def update_ui_text(self):
        """
        Re-apply the translated text to the window title, buttons, labels, etc.
        This is called after changing the language.
        """
        self.root.title(self.t("title"))
        self.reset_button.config(text=self.t("reset_button"))
        self.undo_button.config(text=self.t("undo_button"))
        self.difficulty_button.config(text=self.get_difficulty_button_text())

        current_player = self.t("black_label") if self.current_turn == 'black' else self.t("white_label")
        self.current_player_label.config(text=f"{self.t('current_player_prefix')}{current_player}")

        # If timers haven't started, reset to "00.00"
        if self.player_start_time is None:
            self.player_timer_label.config(text=f"{self.t('black_time_prefix')}00.00")
        if self.ai_start_time is None:
            self.ai_timer_label.config(text=f"{self.t('white_time_prefix')}00.00")

    def center_main_window(self):
        """
        Move the main window to the center of the screen.
        """
        self.root.update_idletasks()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"+{x}+{y}")

    def center_window(self, window, parent):
        """
        Center a popup window relative to its parent window.
        """
        window.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        window_width = window.winfo_width()
        window_height = window.winfo_height()

        position_right = parent_x + int(parent_width / 2 - window_width / 2)
        position_down = parent_y + int(parent_height / 2 - window_height / 2)
        window.geometry(f"+{position_right}+{position_down}")

    def set_default_difficulty(self):
        """
        Based on the current difficulty key (e.g., "medium"), set the number of MCTS simulations and time limit.
        """
        self.mcts_simulations = DIFFICULTY_LEVELS[self.current_difficulty]['simulations']
        self.time_limit = DIFFICULTY_LEVELS[self.current_difficulty]['time_limit']

    def select_difficulty(self):
        """
        Pop up a window for the user to select a difficulty: simple, medium, hard.
        """
        self.difficulty_window = tk.Toplevel(self.root)
        self.difficulty_window.title(self.t("difficulty_window_title"))
        self.difficulty_window.transient(self.root)
        self.difficulty_window.grab_set()

        self.center_window(self.difficulty_window, self.root)

        tk.Label(self.difficulty_window, text=self.t("difficulty_window_label"), font=("Arial", 12)).pack(pady=10)

        self.selected_difficulty = tk.StringVar(value=self.current_difficulty)

        for level_key in DIFFICULTY_LEVELS.keys():
            label_text = self.translations[self.current_language]["difficulty_labels"][level_key]
            tk.Radiobutton(
                self.difficulty_window,
                text=label_text,
                variable=self.selected_difficulty,
                value=level_key,
                font=("Arial", 10)
            ).pack(anchor='w', padx=20)

        tk.Button(self.difficulty_window, text=self.t("ok_button"), command=self.confirm_difficulty).pack(pady=10)

    def confirm_difficulty(self):
        """
        Callback when the user confirms the chosen difficulty.
        Updates the current difficulty and closes the popup window.
        """
        difficulty = self.selected_difficulty.get()
        self.current_difficulty = difficulty
        self.set_default_difficulty()
        self.difficulty_window.destroy()
        self.difficulty_button.config(text=self.get_difficulty_button_text())

    def choose_side(self):
        """
        Ask the user: "Do you want to play first (Black)?"
        If yes => player=black, AI=white
        Otherwise => player=white, AI=black
        Then, if AI goes first, start the AI computation in a background thread.
        """
        answer = messagebox.askquestion(
            self.t("choose_side_title"),
            self.t("choose_side_message"),
            parent=self.root
        )
        if answer == 'yes':
            self.player = 'black'
            self.ai = 'white'
            self.current_turn = self.player
            self.update_status()
            self.start_timer()
        else:
            self.player = 'white'
            self.ai = 'black'
            self.current_turn = self.ai
            self.update_status()
            self.start_timer()
            # If AI moves first, launch a background thread for AI computations
            threading.Thread(target=self.ai_move_thread, daemon=True).start()

    def reset_game(self):
        """
        Reset all game-related data and UI, then prompt for which side the user wants.
        """
        self.board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.canvas.delete("all")
        self.draw_board()
        self.game_over = False
        self.current_turn = 'black'
        self.move_history.clear()
        if self.highlight:
            self.canvas.delete(self.highlight)
            self.highlight = None
        self.reset_timers()
        self.set_default_difficulty()
        self.difficulty_button.config(text=self.get_difficulty_button_text())
        self.center_main_window()
        self.choose_side()

    def draw_board(self):
        """
        Draw the 15x15 grid lines and the "star points" on the board.
        """
        for i in range(BOARD_SIZE):
            # Horizontal line
            self.canvas.create_line(
                BOARD_PADDING, BOARD_PADDING + i * CELL_SIZE,
                BOARD_PADDING + (BOARD_SIZE - 1) * CELL_SIZE, BOARD_PADDING + i * CELL_SIZE
            )
            # Vertical line
            self.canvas.create_line(
                BOARD_PADDING + i * CELL_SIZE, BOARD_PADDING,
                BOARD_PADDING + i * CELL_SIZE, BOARD_PADDING + (BOARD_SIZE - 1) * CELL_SIZE
            )
        # Star points are commonly at (3,3), (3,7), (3,11), etc. for a 15x15 board
        star_points = [3, BOARD_SIZE // 2, BOARD_SIZE - 4]
        for i in star_points:
            for j in star_points:
                x = BOARD_PADDING + i * CELL_SIZE
                y = BOARD_PADDING + j * CELL_SIZE
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='black')

    def click_event(self, event):
        """
        Mouse click event on the board by the user.
        If it's the player's turn, place a stone at the clicked position (if valid).
        Then check for a win, otherwise switch to AI turn.
        """
        if self.game_over:
            return
        if self.current_turn != self.player:
            return

        x = event.x
        y = event.y
        row, col = self.get_nearest_point(x, y)
        # If out of board range or already occupied, ignore
        if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
            return
        if self.board[row][col] != '':
            return

        # Place the player's stone
        self.place_stone(row, col, self.player)
        self.move_history.append((self.player, row, col))
        self.stop_timer()  # Stop the player's timer

        # Check if the player just won
        if self.check_win(row, col, self.player):
            messagebox.showinfo(self.t("game_over_title"), self.t("game_over_win"), parent=self.root)
            self.game_over = True
            return

        # Switch turn to AI
        self.current_turn = self.ai
        self.update_status()
        self.highlight_last_move()
        self.start_timer()

        # Start a new thread for AI's move (computation only), no GUI calls in that thread
        self.root.after(100, lambda: threading.Thread(target=self.ai_move_thread, daemon=True).start())

    def ai_move_thread(self):
        """
        Background thread for AI logic. Finds the best move, then puts that move into the queue.
        """
        move = self.find_best_move()
        if move:
            self.ai_move_queue.put(move)

    def process_ai_move(self):
        """
        Main thread method: Check if there's a move in the AI queue.
        If so, perform the AI move in the main thread (safe for Tkinter).
        This function is called repeatedly by root.after(100, self.process_ai_move).
        """
        try:
            while True:
                # get_nowait() raises queue.Empty if no item
                move = self.ai_move_queue.get_nowait()
                self.perform_ai_move(move[0], move[1])
        except queue.Empty:
            pass

        # Schedule next check
        self.root.after(100, self.process_ai_move)

    def perform_ai_move(self, row, col):
        """
        Perform the AI's move (row, col) in the main thread, update GUI, check for win, etc.
        """
        if self.game_over:
            return

        # Place AI's stone
        self.place_stone(row, col, self.ai)
        self.move_history.append((self.ai, row, col))
        self.stop_timer()  # Stop the AI's timer

        # Check if AI wins
        if self.check_win(row, col, self.ai):
            messagebox.showinfo(self.t("game_over_title"), self.t("game_over_lose"), parent=self.root)
            self.game_over = True
            return

        # Switch back to the player
        self.current_turn = self.player
        self.update_status()
        self.highlight_last_move()
        self.start_timer()

    def get_nearest_point(self, x, y):
        """
        Convert the (x, y) canvas coordinates to a (row, col) on the board.
        If the click is too far from the center of a cell, return (-1, -1).
        """
        col = round((x - BOARD_PADDING) / CELL_SIZE)
        row = round((y - BOARD_PADDING) / CELL_SIZE)
        nearest_x = BOARD_PADDING + col * CELL_SIZE
        nearest_y = BOARD_PADDING + row * CELL_SIZE
        if abs(x - nearest_x) > CELL_SIZE / 2 or abs(y - nearest_y) > CELL_SIZE / 2:
            return -1, -1
        return row, col

    def place_stone(self, row, col, player):
        """
        Place a stone on both the board data and the canvas.
        """
        self.board[row][col] = player
        x = BOARD_PADDING + col * CELL_SIZE
        y = BOARD_PADDING + row * CELL_SIZE
        self.draw_3d_stone(x, y, 'black' if player == 'black' else 'white')

    def draw_3d_stone(self, x, y, color):
        """
        Draw a stone with a 3D effect on the canvas.
        The 'color' parameter should be 'black' or 'white'.
        """
        # Main stone body
        self.canvas.create_oval(
            x - STONE_RADIUS, y - STONE_RADIUS,
            x + STONE_RADIUS, y + STONE_RADIUS,
            fill='black' if color == 'black' else '#EEEEEE',
            outline='',
            tags="stone"
        )
        # Highlight area
        if color == 'black':
            highlight_color = '#AAAAAA'
        else:
            highlight_color = '#FFFFFF'
        self.canvas.create_oval(
            x - STONE_RADIUS + 5, y - STONE_RADIUS + 5,
            x - STONE_RADIUS + 10, y - STONE_RADIUS + 10,
            fill=highlight_color,
            outline='',
            tags="stone"
        )
        # Shadow area
        shadow_color = '#555555' if color == 'black' else '#DDDDDD'
        self.canvas.create_oval(
            x + STONE_RADIUS - 10, y + STONE_RADIUS - 10,
            x + STONE_RADIUS - 5, y + STONE_RADIUS - 5,
            fill=shadow_color,
            outline='',
            tags="stone"
        )

    def check_win(self, row, col, player):
        """
        Check if placing a stone for 'player' at (row, col) results in 5 in a row.
        Check horizontal, vertical, and two diagonal directions.
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            # Check in the "forward" direction
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            # Check in the "reverse" direction
            r, c = row - dr, col - dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            # If at least 5, it's a win
            if count >= 5:
                return True
        return False

    def find_best_move(self):
        """
        Use MCTS to find the best (row, col) move for the AI.
        """
        return mcts_search(self.board, self.ai, self.player, self.mcts_simulations, self.time_limit)

    def undo_move(self):
        """
        Undo the last two moves (AI + player) if possible, unless the game is over.
        """
        if not self.move_history:
            messagebox.showinfo(self.t("no_undo_title"), self.t("no_undo_message"), parent=self.root)
            return
        if self.game_over:
            messagebox.showinfo(self.t("no_undo_title"), self.t("game_end_no_undo_message"), parent=self.root)
            return

        # Remove the last move
        last_player, row, col = self.move_history.pop()
        self.board[row][col] = ''
        self.redraw_board()
        self.highlight_last_move()

        # If that was the AI's move, also remove the player's move
        if last_player == self.ai and self.move_history:
            last_player, row, col = self.move_history.pop()
            self.board[row][col] = ''
            self.redraw_board()
            self.highlight_last_move()

        self.current_turn = self.player
        self.update_status()
        self.stop_timer()
        self.start_timer()

    def redraw_board(self):
        """
        Clear all stones from the canvas and redraw them according to self.board.
        """
        self.canvas.delete("stone")
        self.canvas.delete("highlight")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col]:
                    self.place_stone(row, col, self.board[row][col])
        if self.highlight:
            self.canvas.delete(self.highlight)
            self.highlight = None

    def highlight_last_move(self):
        """
        Draw a red highlight around the most recent move.
        """
        if self.highlight:
            self.canvas.delete(self.highlight)
            self.highlight = None
        if not self.move_history:
            return
        _, row, col = self.move_history[-1]
        x = BOARD_PADDING + col * CELL_SIZE
        y = BOARD_PADDING + row * CELL_SIZE
        self.highlight = self.canvas.create_oval(
            x - STONE_RADIUS - 2, y - STONE_RADIUS - 2,
            x + STONE_RADIUS + 2, y + STONE_RADIUS + 2,
            outline='red', width=2, tags="highlight"
        )

    def update_status(self):
        """
        Update the label to show whose turn it is.
        """
        current_player = self.t("black_label") if self.current_turn == 'black' else self.t("white_label")
        self.current_player_label.config(text=f"{self.t('current_player_prefix')}{current_player}")

    def start_timer(self):
        """
        Start (or resume) the timer for whichever side's turn it is: player or AI.
        """
        if self.current_turn == self.player:
            self.player_start_time = time.time()
            self.update_player_timer()
        else:
            self.ai_start_time = time.time()
            self.update_ai_timer()

    def stop_timer(self):
        """
        Stop the currently running timer (player or AI) and update the label with the elapsed time.
        """
        if self.current_turn == self.player and self.player_start_time:
            elapsed = time.time() - self.player_start_time
            self.player_timer_label.config(text=f"{self.t('black_time_prefix')}{self.format_time(elapsed)}")
            self.player_start_time = None
        elif self.current_turn == self.ai and self.ai_start_time:
            elapsed = time.time() - self.ai_start_time
            self.ai_timer_label.config(text=f"{self.t('white_time_prefix')}{self.format_time(elapsed)}")
            self.ai_start_time = None

    def reset_timers(self):
        """
        Reset both timers to "00.00" and clear start times.
        """
        self.player_start_time = None
        self.ai_start_time = None
        self.player_timer_label.config(text=f"{self.t('black_time_prefix')}00.00")
        self.ai_timer_label.config(text=f"{self.t('white_time_prefix')}00.00")

    def update_player_timer(self):
        """
        Continuously update the player's timer every 100ms while it is running.
        """
        if self.player_start_time:
            elapsed = time.time() - self.player_start_time
            self.player_timer_label.config(
                text=f"{self.t('black_time_prefix')}{self.format_time(elapsed)}"
            )
            self.root.after(100, self.update_player_timer)

    def update_ai_timer(self):
        """
        Continuously update the AI's timer every 100ms while it is running.
        """
        if self.ai_start_time:
            elapsed = time.time() - self.ai_start_time
            self.ai_timer_label.config(
                text=f"{self.t('white_time_prefix')}{self.format_time(elapsed)}"
            )
            self.root.after(100, self.update_ai_timer)

    def format_time(self, seconds):
        """
        Convert a time in seconds to a string like "SS.mm".
        Only shows seconds and two decimal places for milliseconds.
        """
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        millis = int((seconds - int(seconds)) * 100)
        return f"{secs:02d}.{millis:02d}"


# ---------------------
# MCTS-related functions
# ---------------------

def mcts_search(board, ai_player, human_player, simulations, time_limit):
    """
    Main entry for the Monte Carlo Tree Search.
    :param board: 2D list (15x15) representing the current board state
    :param ai_player: 'black' or 'white' representing the AI's color
    :param human_player: 'black' or 'white' representing the human's color
    :param simulations: number of MCTS simulations to run
    :param time_limit: max time (in seconds) for the MCTS
    :return: The best move (row, col) for the AI
    """
    start_time = time.time()
    end_time = start_time + time_limit

    # Create the root node for MCTS
    root = MCTSNode(
        board=copy.deepcopy(board),
        player=ai_player,
        ai_player=ai_player,
        human_player=human_player
    )

    # Use multiprocessing to parallelize simulations
    with Pool(processes=cpu_count()) as pool:
        # Each simulation runs the 'simulate' function with the same root, players, and end_time
        results = pool.starmap(
            simulate,
            [(root, ai_player, human_player, end_time) for _ in range(simulations)]
        )

    # Tally how many times each move was returned from simulations
    move_scores = {}
    for move in results:
        if move is not None:
            move_scores[move] = move_scores.get(move, 0) + 1

    # If no moves found by MCTS (very rare) or no expansions, pick a random valid move
    if not move_scores:
        possible_moves = get_possible_moves(board)
        return random.choice(possible_moves)

    # Otherwise choose the move that appeared the most in the simulations
    best_move = max(move_scores, key=move_scores.get)
    return best_move


class MCTSNode:
    """
    A node in the MCTS tree. Stores a board state, the player to move, and statistics.
    """
    def __init__(self, board, player, ai_player, human_player, move=None, parent=None):
        self.board = board                # The 15x15 board state
        self.player = player              # Which player is to move at this node
        self.ai_player = ai_player
        self.human_player = human_player
        self.move = move                  # The move (row, col) that led to this node
        self.parent = parent
        self.children = {}                # A dict of move -> MCTSNode
        self.wins = 0                     # Accumulated wins (for the AI) during backpropagation
        self.visits = 0                   # Number of times this node is visited

    def is_fully_expanded(self):
        """
        Check if this node has expanded all possible moves (children).
        """
        return len(self.children) == len(get_possible_moves(self.board))

    def best_child(self, c_param=1.414):
        """
        Use the UCB (Upper Confidence Bound) formula to select the best child:
        score = exploitation + exploration
               = (child.wins / child.visits) + c_param * sqrt(log(self.visits) / child.visits)
        c_param is typically sqrt(2).
        """
        best_score = -INF
        best_move = None
        for move, child in self.children.items():
            if child.visits == 0:
                # If the child has 0 visits, it might be prioritized automatically
                return child
            exploitation = child.wins / child.visits
            exploration = c_param * math.sqrt(math.log(self.visits) / child.visits)
            score = exploitation + exploration
            if score > best_score:
                best_score = score
                best_move = move
        return self.children[best_move] if best_move else None


def simulate(node, ai_player, human_player, end_time):
    """
    One complete MCTS simulation:
    1) Selection: Follow best_child() down the tree until we reach a node that isn't fully expanded
    2) Expansion: Create a new child from a random possible move
    3) Simulation: Play moves randomly until there's a winner or time is up
    4) Backpropagation: Update the visited nodes with wins/visits
    Return the move that was selected in the expansion step (or None if none).
    """
    current_node = node
    board = copy.deepcopy(node.board)
    player = current_node.player

    # 1) SELECTION
    while current_node.is_fully_expanded() and current_node.children:
        current_node = current_node.best_child()
        if current_node and current_node.move:
            # Apply the move
            board[current_node.move[0]][current_node.move[1]] = current_node.player
            # Toggle the player between ai_player and human_player
            player = ai_player if current_node.player == human_player else human_player
        else:
            break

    # 2) EXPANSION
    possible_moves = get_possible_moves(board)
    if possible_moves and current_node:
        move = random.choice(possible_moves)
        board[move[0]][move[1]] = player
        child_node = MCTSNode(
            board=copy.deepcopy(board),
            player=ai_player if player == human_player else human_player,
            ai_player=ai_player,
            human_player=human_player,
            move=move,
            parent=current_node
        )
        current_node.children[move] = child_node
        player = ai_player if player == human_player else human_player
    else:
        move = None

    # 3) SIMULATION (random playout)
    winner = None
    while True:
        # Check if there's a winner after the last move
        if move is not None and check_win(board, move, ai_player):
            winner = ai_player
            break
        elif move is not None and check_win(board, move, human_player):
            winner = human_player
            break

        # If no more moves left, it's a draw
        possible_moves = get_possible_moves(board)
        if not possible_moves:
            break

        # Randomly pick the next move
        move = random.choice(possible_moves)
        board[move[0]][move[1]] = player

        # Check again if there's a winner
        if check_win(board, move, player):
            winner = player
            break

        # Switch player
        player = ai_player if player == human_player else human_player

        # If time is exceeded, break early
        if time.time() > end_time:
            break

    # 4) BACKPROPAGATION
    while current_node:
        current_node.visits += 1
        if winner == ai_player:
            current_node.wins += 1
        elif winner == human_player:
            current_node.wins -= 1
        current_node = current_node.parent

    return move


def check_win(board, move, player):
    """
    Check if placing 'player' at 'move' (row, col) results in 5 in a row.
    For MCTS simulation usage.
    """
    if move is None:
        return False
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    row, col = move
    for dr, dc in directions:
        count = 1
        # Forward direction
        r, c = row + dr, col + dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            count += 1
            r += dr
            c += dc
        # Reverse direction
        r, c = row - dr, col - dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            count += 1
            r -= dr
            c -= dc
        if count >= 5:
            return True
    return False


def get_possible_moves(board):
    """
    Return all "reasonable" empty positions on the board, i.e., positions
    within 2 cells of any existing stone. If the board is empty, return the center position.
    """
    moves = set()
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] != '':
                # For each occupied cell, consider empty cells within a 2-cell radius
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        r, c = row + dr, col + dc
                        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == '':
                            moves.add((r, c))
    # If the board is totally empty, just return the center
    if not moves:
        return [(BOARD_SIZE // 2, BOARD_SIZE // 2)]
    return list(moves)


def main():
    """
    Application entry point. Create the main Tk window and start the Gomoku game.
    """
    root = tk.Tk()
    game = Gomoku(root)
    root.mainloop()


if __name__ == "__main__":
    main()
