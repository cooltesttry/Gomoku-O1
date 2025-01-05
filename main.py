import tkinter as tk
from tkinter import messagebox
import time
from multiprocessing import Pool, cpu_count
import random
import copy
import math
import threading

# ---------------------------
# Global Constants
# ---------------------------

# Board size (15x15)
BOARD_SIZE = 15
# Pixel size of each cell
CELL_SIZE = 40
# Padding for board drawing
BOARD_PADDING = 20

# Stone radius
STONE_RADIUS = 15

# An infinitely large value, used for comparison in the algorithm
INF = float('inf')

# Difficulty levels and corresponding MCTS simulation times and time limits
DIFFICULTY_LEVELS = {
    'simple': {'simulations': 500, 'time_limit': 2},
    'medium': {'simulations': 1000, 'time_limit': 5},
    'hard': {'simulations': 3000, 'time_limit': 12},
}

class Gomoku:
    """
    The main Gomoku class that integrates UI drawing and game logic 
    (including AI thinking and player interaction).
    """
    # Multi-language dictionary (including titles, buttons, prompts, etc.)
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
        Initialize the main game window and some key variables, 
        including board drawing, control buttons, and difficulty options.
        """
        self.root = root
        # Default language set to English ("en"), can switch manually
        self.current_language = "en"

        # Current AI difficulty, internally only uses the English key
        self.current_difficulty = "medium"

        # Set the main window title (according to the language dictionary)
        self.root.title(self.t("title"))
        # Calculate the canvas size based on board size and padding
        self.canvas_size = CELL_SIZE * (BOARD_SIZE - 1) + 2 * BOARD_PADDING

        # Create a Canvas for the board area with an ivory-like background color
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg='#E0C9A5')
        self.canvas.pack()

        # Bind the left mouse button click event
        self.canvas.bind("<Button-1>", self.click_event)

        # -------------------------
        # Control area: language + feature buttons
        # -------------------------
        # Create a container Frame to hold language selection and feature buttons
        self.control_frame = tk.Frame(root, bg="#F8F8F8")
        self.control_frame.pack(fill="x", side="bottom", padx=10, pady=10)

        # (1) Language selection area - on the left
        self.language_frame = tk.Frame(self.control_frame, bg="#F8F8F8")
        self.language_frame.pack(side="left")

        # Show "Lang:" label
        tk.Label(self.language_frame, text="Lang:", bg="#F8F8F8").pack(side="left", padx=(0, 5))

        # Use StringVar to track the selected language
        self.selected_language = tk.StringVar(value=self.current_language)
        # Available languages: Chinese, English, Spanish, French
        languages = [("中文", "zh"), ("EN", "en"), ("ES", "es"), ("FR", "fr")]
        # Create radio buttons in a loop
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

        # (2) Feature buttons area - on the right
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

        # Difficulty selection button, text will show "Difficulty (current level)"
        self.difficulty_button = tk.Button(
            self.button_frame,
            text=self.get_difficulty_button_text(),
            command=self.select_difficulty,
            bg="#ECECEC",
            activebackground="#D0D0D0",
            relief="groove"
        )
        self.difficulty_button.pack(side="left", padx=5)

        # -------------------------
        # Status bar area (shows current player, timers, etc.)
        # -------------------------
        self.status_frame = tk.Frame(root)
        self.status_frame.pack(pady=10)

        # Current player label, default shows "Black"
        self.current_player_label = tk.Label(
            self.status_frame,
            text=f"{self.t('current_player_prefix')}{self.t('black_label')}",
            font=("Arial", 12)
        )
        self.current_player_label.grid(row=0, column=0, padx=10)

        # Timer labels: black & white, used to show time spent on each move
        self.player_timer_label = tk.Label(
            self.status_frame,
            text=f"{self.t('black_time_prefix')}00.00",
            font=("Arial", 12)
        )
        self.player_timer_label.grid(row=0, column=1, padx=10)

        self.ai_timer_label = tk.Label(
            self.status_frame,
            text=f"{self.t('white_time_prefix')}00.00",
            font=("Arial", 12)
        )
        self.ai_timer_label.grid(row=0, column=2, padx=10)

        # Timer start times: for player and AI respectively
        self.player_start_time = None
        self.ai_start_time = None

        # -------------------------
        # Game logic-related variables
        # -------------------------
        # Define a 2D list to store the board state: each element can be 'black', 'white', or ''
        self.board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.game_over = False            # Indicates if the game is over
        self.current_turn = 'black'       # Whose turn it is
        self.move_history = []            # Move history for undo purposes

        # Marker for highlighting the last move
        self.highlight = None

        # Draw the initial board lines and star points
        self.draw_board()
        # Set MCTS simulation times and time limit according to current difficulty
        self.set_default_difficulty()
        # Center the main window
        self.center_main_window()
        # Ask the player whether to go first
        self.choose_side()

    def t(self, key):
        """
        Retrieve the translated text according to the current language.
        If the key is not found in the dictionary, return the key itself.
        """
        return self.translations[self.current_language].get(key, key)

    def get_difficulty_button_text(self):
        """
        Text for the difficulty selection button. 
        Will retrieve different difficulty labels based on the current language.
        Example: Difficulty (Easy)
        """
        diff_label = self.translations[self.current_language]["difficulty_labels"][self.current_difficulty]
        return f"{self.t('difficulty_button')} ({diff_label})"

    def set_language(self, lang_code):
        """
        Update the current language and redraw all UI text.
        """
        self.current_language = lang_code
        self.update_ui_text()

    def update_ui_text(self):
        """
        When switching languages, update window title, button text, and status bar text.
        Does not restart the game, only updates the displayed text.
        """
        self.root.title(self.t("title"))
        self.reset_button.config(text=self.t("reset_button"))
        self.undo_button.config(text=self.t("undo_button"))
        self.difficulty_button.config(text=self.get_difficulty_button_text())
        # Update status bar text
        current_player = self.t("black_label") if self.current_turn == 'black' else self.t("white_label")
        self.current_player_label.config(text=f"{self.t('current_player_prefix')}{current_player}")

        # If the timer hasn't started yet, use the initial text to replace
        if self.player_start_time is None:
            self.player_timer_label.config(text=f"{self.t('black_time_prefix')}00.00")
        if self.ai_start_time is None:
            self.ai_timer_label.config(text=f"{self.t('white_time_prefix')}00.00")

    def center_main_window(self):
        """
        Make the main window display in the center of the screen.
        First call update_idletasks() to compute size and position, then move the window.
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
        Make the pop-up window (window) centered relative to its parent (parent).
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
        Based on self.current_difficulty, retrieve MCTS simulation times (simulations) 
        and time limit (time_limit) from DIFFICULTY_LEVELS.
        """
        self.mcts_simulations = DIFFICULTY_LEVELS[self.current_difficulty]['simulations']
        self.time_limit = DIFFICULTY_LEVELS[self.current_difficulty]['time_limit']

    def select_difficulty(self):
        """
        Pop up a window allowing the player to choose AI difficulty (simple, medium, hard).
        """
        # Create a pop-up window
        self.difficulty_window = tk.Toplevel(self.root)
        self.difficulty_window.title(self.t("difficulty_window_title"))
        self.difficulty_window.transient(self.root)
        self.difficulty_window.grab_set()

        # Center the pop-up window
        self.center_window(self.difficulty_window, self.root)

        tk.Label(self.difficulty_window, text=self.t("difficulty_window_label"), font=("Arial", 12)).pack(pady=10)

        # Use StringVar to record the selected difficulty
        self.selected_difficulty = tk.StringVar(value=self.current_difficulty)
        # Create a radio button for each difficulty
        for level_key in DIFFICULTY_LEVELS.keys():
            label_text = self.translations[self.current_language]["difficulty_labels"][level_key]
            tk.Radiobutton(
                self.difficulty_window,
                text=label_text,
                variable=self.selected_difficulty,
                value=level_key,
                font=("Arial", 10)
            ).pack(anchor='w', padx=20)

        # When "OK" is clicked, call confirm_difficulty
        tk.Button(self.difficulty_window, text=self.t("ok_button"), command=self.confirm_difficulty).pack(pady=10)

    def confirm_difficulty(self):
        """
        When the player clicks "OK" in the difficulty selection window, 
        update the current difficulty and refresh button text.
        """
        difficulty = self.selected_difficulty.get()
        self.current_difficulty = difficulty
        self.set_default_difficulty()  # Update MCTS parameters
        self.difficulty_window.destroy()
        # Refresh the text on the difficulty selection button
        self.difficulty_button.config(text=self.get_difficulty_button_text())

    def choose_side(self):
        """
        Ask the player whether to go first (black). 
        If the player chooses 'yes', then player=black, AI=white; 
        otherwise player=white, AI=black.
        """
        answer = messagebox.askquestion(
            self.t("choose_side_title"),
            self.t("choose_side_message"),
            parent=self.root
        )
        if answer == 'yes':
            # Player goes first
            self.player = 'black'
            self.ai = 'white'
            self.current_turn = self.player
            self.update_status()
            self.start_timer()
        else:
            # AI goes first
            self.player = 'white'
            self.ai = 'black'
            self.current_turn = self.ai
            self.update_status()
            self.start_timer()
            # Use after and multithreading to execute AI logic, avoiding blocking the main thread
            self.root.after(100, lambda: threading.Thread(target=self.ai_move_thread).start())

    def reset_game(self):
        """
        Restart the game: clear the board, state, and history, then ask again who goes first.
        """
        self.board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.canvas.delete("all")   # Remove all stones and lines
        self.draw_board()           # Redraw the board
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
        Draw the grid lines and star points of the board.
        15 lines horizontally and vertically, plus star points at (3,7,11).
        """
        for i in range(BOARD_SIZE):
            # Draw horizontal lines
            self.canvas.create_line(
                BOARD_PADDING, BOARD_PADDING + i * CELL_SIZE,
                BOARD_PADDING + (BOARD_SIZE - 1) * CELL_SIZE, BOARD_PADDING + i * CELL_SIZE
            )
            # Draw vertical lines
            self.canvas.create_line(
                BOARD_PADDING + i * CELL_SIZE, BOARD_PADDING,
                BOARD_PADDING + i * CELL_SIZE, BOARD_PADDING + (BOARD_SIZE - 1) * CELL_SIZE
            )
        # Draw star points: located at [3,7,11] for a 15x15 board
        star_points = [3, BOARD_SIZE // 2, BOARD_SIZE - 4]
        for i in star_points:
            for j in star_points:
                x = BOARD_PADDING + i * CELL_SIZE
                y = BOARD_PADDING + j * CELL_SIZE
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='black')

    def click_event(self, event):
        """
        Player click event on the board: determine the clicked position and place a stone, 
        then call AI or check for a winner.
        """
        # If the game is over, clicking is invalid
        if self.game_over:
            return
        # If it's not the player's turn (i.e., AI's turn), clicking is invalid
        if self.current_turn != self.player:
            return

        # Compute the (row,col) index based on the clicked pixel coordinates
        x = event.x
        y = event.y
        row, col = self.get_nearest_point(x, y)
        # If it goes beyond the board range, ignore
        if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
            return
        # If there's already a stone in that position, cannot place another
        if self.board[row][col] != '':
            return

        # Player places the stone
        self.place_stone(row, col, self.player)
        # Add the move to the history
        self.move_history.append((self.player, row, col))

        # Stop the player's timer
        self.stop_timer()

        # Check if the player has already made five in a row
        if self.check_win(row, col, self.player):
            messagebox.showinfo(self.t("game_over_title"), self.t("game_over_win"), parent=self.root)
            self.game_over = True
            return

        # Switch to AI's turn
        self.current_turn = self.ai
        self.update_status()
        # Highlight the latest move
        self.highlight_last_move()
        # Start the AI timer
        self.start_timer()
        # Execute AI thinking asynchronously to avoid blocking the UI
        self.root.after(100, lambda: threading.Thread(target=self.ai_move_thread).start())

    def ai_move_thread(self):
        """
        AI thinking thread function: use MCTS or other algorithms to find the best move, then place the stone.
        """
        move = self.find_best_move()
        if move:
            self.root.after(0, self.perform_ai_move, move[0], move[1])

    def perform_ai_move(self, row, col):
        """
        After the AI calculates a move, actually place the stone on the UI.
        """
        if self.game_over:
            return
        # AI places the stone
        self.place_stone(row, col, self.ai)
        self.move_history.append((self.ai, row, col))

        # Stop the AI timer
        self.stop_timer()

        # Check if AI wins
        if self.check_win(row, col, self.ai):
            messagebox.showinfo(self.t("game_over_title"), self.t("game_over_lose"), parent=self.root)
            self.game_over = True
            return

        # Switch back to the player's turn
        self.current_turn = self.player
        self.update_status()
        self.highlight_last_move()
        self.start_timer()

    def get_nearest_point(self, x, y):
        """
        Map the mouse click pixel coordinates to the board grid's (row,col).
        First convert (x,y) to row,col indices, then check if it's in a valid range.
        """
        col = round((x - BOARD_PADDING) / CELL_SIZE)
        row = round((y - BOARD_PADDING) / CELL_SIZE)
        nearest_x = BOARD_PADDING + col * CELL_SIZE
        nearest_y = BOARD_PADDING + row * CELL_SIZE
        # If the click is too far from the grid center, treat as invalid
        if abs(x - nearest_x) > CELL_SIZE / 2 or abs(y - nearest_y) > CELL_SIZE / 2:
            return -1, -1
        return row, col

    def place_stone(self, row, col, player):
        """
        Place a stone on both the board data (self.board) and the UI.
        """
        # Update the board state in memory
        self.board[row][col] = player
        # Compute the pixel coordinates for the center of this cell
        x = BOARD_PADDING + col * CELL_SIZE
        y = BOARD_PADDING + row * CELL_SIZE
        # Draw a 3D-looking stone
        self.draw_3d_stone(x, y, 'black' if player == 'black' else 'white')

    def draw_3d_stone(self, x, y, color):
        """
        Draw a stone that simulates a 3D effect, including the stone itself, 
        a highlight part, and a shadow part.
        The color parameter accepts only 'black' or 'white'.
        """
        # Main body of the stone
        self.canvas.create_oval(
            x - STONE_RADIUS, y - STONE_RADIUS,
            x + STONE_RADIUS, y + STONE_RADIUS,
            fill='black' if color == 'black' else '#EEEEEE',
            outline='',
            tags="stone"
        )
        # Highlight part
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
        # Shadow part
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
        Check if player forms five in a row after placing a stone at (row, col).
        Only need to count in 4 directions (horizontal, vertical, diagonal, anti-diagonal).
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            # Forward direction
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            # Reverse direction
            r, c = row - dr, col - dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                return True
        return False

    def find_best_move(self):
        """
        Call MCTS search to return the AI's chosen (row, col).
        """
        return mcts_search(self.board, self.ai, self.player, self.mcts_simulations, self.time_limit)

    def undo_move(self):
        """
        The undo feature: one undo action will remove both the player's and the AI's moves 
        (if the AI already played).
        """
        if not self.move_history:
            messagebox.showinfo(self.t("no_undo_title"), self.t("no_undo_message"), parent=self.root)
            return
        # If the game is over, can't undo
        if self.game_over:
            messagebox.showinfo(self.t("no_undo_title"), self.t("game_end_no_undo_message"), parent=self.root)
            return

        # First undo the last move (could be AI's or player's)
        last_player, row, col = self.move_history.pop()
        self.board[row][col] = ''
        self.redraw_board()
        self.highlight_last_move()

        # If the undone move was the AI's, also undo the player's last move
        if last_player == self.ai and self.move_history:
            last_player, row, col = self.move_history.pop()
            self.board[row][col] = ''
            self.redraw_board()
            self.highlight_last_move()

        # After undoing, give the turn back to the player
        self.current_turn = self.player
        self.update_status()
        # Restart the player's timer
        self.stop_timer()
        self.start_timer()

    def redraw_board(self):
        """
        According to the state in self.board, first delete all stone graphics, 
        then redraw all placed stones.
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
        Use a red circle to highlight the position of the last move.
        """
        if self.highlight:
            self.canvas.delete(self.highlight)
            self.highlight = None
        if not self.move_history:
            return
        last_move = self.move_history[-1]
        _, row, col = last_move
        x = BOARD_PADDING + col * CELL_SIZE
        y = BOARD_PADDING + row * CELL_SIZE
        self.highlight = self.canvas.create_oval(
            x - STONE_RADIUS - 2, y - STONE_RADIUS - 2,
            x + STONE_RADIUS + 2, y + STONE_RADIUS + 2,
            outline='red', width=2, tags="highlight"
        )

    def update_status(self):
        """
        Update the status bar: display whether the current player is "Black" or "White".
        """
        current_player = self.t("black_label") if self.current_turn == 'black' else self.t("white_label")
        self.current_player_label.config(text=f"{self.t('current_player_prefix')}{current_player}")

    def start_timer(self):
        """
        Based on whose turn it is, start the corresponding timer (player or AI).
        """
        if self.current_turn == self.player:
            self.player_start_time = time.time()
            self.update_player_timer()
        else:
            self.ai_start_time = time.time()
            self.update_ai_timer()

    def stop_timer(self):
        """
        After a player finishes a move, stop that player's timer and update the display.
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
        Reset the timer display to 00.00 and clear the start times.
        """
        self.player_start_time = None
        self.ai_start_time = None
        self.player_timer_label.config(text=f"{self.t('black_time_prefix')}00.00")
        self.ai_timer_label.config(text=f"{self.t('white_time_prefix')}00.00")

    def update_player_timer(self):
        """
        Recursively update the player's timer label every 0.1s until stop_timer is called.
        """
        if self.player_start_time:
            elapsed = time.time() - self.player_start_time
            self.player_timer_label.config(
                text=f"{self.t('black_time_prefix')}{self.format_time(elapsed)}"
            )
            self.root.after(100, self.update_player_timer)

    def update_ai_timer(self):
        """
        Recursively update the AI's timer label every 0.1s until stop_timer is called.
        """
        if self.ai_start_time:
            elapsed = time.time() - self.ai_start_time
            self.ai_timer_label.config(
                text=f"{self.t('white_time_prefix')}{self.format_time(elapsed)}"
            )
            self.root.after(100, self.update_ai_timer)

    def format_time(self, seconds):
        """
        Format seconds into SS.mm form (only display seconds and milliseconds).
        """
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        millis = int((seconds - int(seconds)) * 100)
        return f"{secs:02d}.{millis:02d}"

# ---------------------
# MCTS-related functions below
# ---------------------

def mcts_search(board, ai_player, human_player, simulations, time_limit):
    """
    Perform an MCTS search on the given board, with ai_player as AI and human_player as the opponent.
    'simulations' is the number of MCTS simulations, and 'time_limit' is the search time limit.
    Returns the (row, col) chosen by the AI.
    """
    start_time = time.time()
    end_time = start_time + time_limit

    # Create the root node, the player is the AI by default
    root = MCTSNode(
        board=copy.deepcopy(board),
        player=ai_player,
        ai_player=ai_player,
        human_player=human_player
    )

    # Use multiprocessing for parallel simulations
    with Pool(processes=cpu_count()) as pool:
        results = pool.starmap(
            simulate,
            [(root, ai_player, human_player, end_time) for _ in range(simulations)]
        )

    move_scores = {}
    # Count how many times each move is returned by simulations
    for move in results:
        if move is not None:
            if move in move_scores:
                move_scores[move] += 1
            else:
                move_scores[move] = 1

    # If all simulations yield no result (or no valid move), randomly choose one
    if not move_scores:
        possible_moves = get_possible_moves(board)
        return random.choice(possible_moves)

    # Otherwise, choose the move with the highest count as the final result
    best_move = max(move_scores, key=move_scores.get)
    return best_move

class MCTSNode:
    """
    MCTS node class: contains a board state and the player who will move on this node.
    """
    def __init__(self, board, player, ai_player, human_player, move=None, parent=None):
        self.board = board                    # Board state (2D list)
        self.player = player                  # Which player is about to move in this node
        self.ai_player = ai_player            # Which side is AI
        self.human_player = human_player      # Which side is human
        self.move = move                      # The move (row, col) from the parent node to this node
        self.parent = parent                  # Parent node
        self.children = {}                    # Mapping of move -> MCTSNode for all child nodes
        self.wins = 0                         # Number of wins (accumulated during backpropagation)
        self.visits = 0                       # Number of times this node is visited

    def is_fully_expanded(self):
        """
        Check whether the current node is fully expanded:
        i.e., the number of children == the number of possible moves on the current board.
        """
        return len(self.children) == len(get_possible_moves(self.board))

    def best_child(self, c_param=1.414):
        """
        Use the UCB formula to select the best child node: 
        score = exploitation + exploration
        exploitation = child.wins / child.visits
        exploration = c_param * sqrt(log(self.visits) / child.visits)
        c_param is usually sqrt(2).
        """
        best_score = -INF
        best_move = None
        for move, child in self.children.items():
            if child.visits == 0:
                # If child is never visited, prioritize returning it for expansion
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
    One MCTS simulation includes:
    1. Selection: traverse downward through best_child() until finding a node that can be expanded or has no children
    2. Expansion: randomly choose a possible move to create a new child node
    3. Simulation: randomly play moves until the game ends or time runs out
    4. Backpropagation: propagate the result (win/lose) up the tree and update wins/visits
    Returns the move from this simulation.
    """
    current_node = node
    board = copy.deepcopy(node.board)
    player = current_node.player

    # --------------------
    # 1. Selection
    # --------------------
    # Keep walking down child nodes via best_child() until a node is not fully expanded or has no children
    while current_node.is_fully_expanded() and current_node.children:
        current_node = current_node.best_child()
        if current_node and current_node.move:
            # Apply this child node's move to the board
            board[current_node.move[0]][current_node.move[1]] = current_node.player
            # Switch the player (AI->Human or Human->AI)
            player = ai_player if current_node.player == human_player else human_player
        else:
            break

    # --------------------
    # 2. Expansion
    # --------------------
    # Find all possible moves, then randomly select one to expand
    possible_moves = get_possible_moves(board)
    if possible_moves and current_node:
        move = random.choice(possible_moves)
        board[move[0]][move[1]] = player
        # Create a new child node
        child_node = MCTSNode(
            board=copy.deepcopy(board),
            player=ai_player if player == human_player else human_player,
            ai_player=ai_player,
            human_player=human_player,
            move=move,
            parent=current_node
        )
        # Insert this child node into current_node's children
        current_node.children[move] = child_node
        # Next player
        player = ai_player if player == human_player else human_player
    else:
        move = None

    # --------------------
    # 3. Simulation
    # --------------------
    # Randomly simulate the game until there is a winner, no available moves, or timeout
    winner = None
    while True:
        # Check if AI or Human wins after the last move
        if move is not None and check_win(board, move, ai_player):
            winner = ai_player
            break
        elif move is not None and check_win(board, move, human_player):
            winner = human_player
            break

        possible_moves = get_possible_moves(board)
        if not possible_moves:
            # No moves left => draw
            break

        # Randomly select one from the remaining moves
        move = random.choice(possible_moves)
        board[move[0]][move[1]] = player

        # Check if the new move forms a win
        if check_win(board, move, player):
            winner = player
            break

        # Switch player
        player = ai_player if player == human_player else human_player

        # If time limit is exceeded, break
        if time.time() > end_time:
            break

    # --------------------
    # 4. Backpropagation
    # --------------------
    # Traverse up from the current node to the parent, updating visits and wins
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
    On the given board, determine if placing a stone at 'move' 
    causes 'player' to form five in a row.
    Similar to Gomoku.check_win but used here for MCTS simulation.
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
    Get all "reasonable" moves (empty positions) on the given board, 
    i.e. empty spaces within 2 grids of any existing stone.
    If the board is completely empty, default to returning the center point.
    """
    moves = set()
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] != '':
                # For every existing stone, any empty position within 2 grids around it can be a candidate move
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        r, c = row + dr, col + dc
                        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == '':
                            moves.add((r, c))
    # If the board is completely empty, return the center point
    if not moves:
        return [(BOARD_SIZE // 2, BOARD_SIZE // 2)]
    return list(moves)

def main():
    """
    Entry point of the program, creates the Tk main window and starts the Gomoku game.
    """
    root = tk.Tk()
    game = Gomoku(root)
    root.mainloop()

if __name__ == "__main__":
    main()
