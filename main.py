import tkinter as tk  # Tkinter is a standard GUI library in Python
from tkinter import messagebox  # Used for showing pop-up messages
from PIL import Image, ImageTk  # PIL (Pillow) for image processing
import time  # Used for time measurement, such as timers
from multiprocessing import Pool, cpu_count, freeze_support  # Multiprocessing functionalities
import random  # For random selection (e.g., random moves in MCTS)
import os  # Used for operating system interactions, such as path handling
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # Hide the pygame welcome message
import pygame  # For playing sound effects
import copy  # Used to deep copy Python objects (board states)
import math  # Mathematical functions, e.g., for sqrt or log
import threading  # For running AI computations in separate threads
import queue  # A thread-safe queue to communicate between threads
import sys  # Access to system-specific parameters and functions
from array import array  # Efficient arrays of numeric values for board states

def resource_path(relative_path):
    """Get the absolute path of the resource file"""
    # This function ensures that resource files (e.g., images, sounds) can be found
    # whether the script is run directly or packaged (e.g., with PyInstaller).
    if hasattr(sys, '_MEIPASS'):
        # If running after packaging, use the temporary _MEIPASS folder
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running in normal mode
        current_directory = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_directory, relative_path)

# ---------------------------
# Global Constants
# ---------------------------

BOARD_SIZE = 15  # The board is 15 x 15
CELL_SIZE = 40   # Each cell in the board is 40 pixels
BOARD_PADDING = 20  # Extra space around the board in pixels
STONE_RADIUS = 15   # The radius of each stone in pixels
BG_COLOR = None  # Background color for the main window (None = default)

INF = float('inf')  # Infinity, used in MCTS for initialization

# Difficulty settings with MCTS-related parameters:
# - 'simple': fewer simulations, lower time limit
# - 'medium': moderate simulations, moderate time limit
# - 'hard': large number of simulations, higher time limit
DIFFICULTY_LEVELS = {
    'simple': {'simulations': 500, 'time_limit': 2},
    'medium': {'simulations': 1200, 'time_limit': 7},
    'hard': {'simulations': 4000, 'time_limit': 15},
}

DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]
FIVE_IN_A_ROW = 0
OPEN_FOUR = 1
FOUR_WITH_GAP = 2
CLOSED_FOUR = 3
OPEN_THREE = 4
OPEN_THREE_WITH_GAP = 5
OPEN_TWO = 6
OPEN_TWO_WITH_GAP = 7

def check_pattern(arr , row, col, player):
    """
    Check if placing 'player' stone at (row, col) results in a five-in-a-row (horizontal, vertical, diagonals).
    """
    pattern = [0, 0, 0, 0, 0, 0, 0, 0]
    for dr, dc in DIRECTIONS:
        count = 1
        e1 = False
        e2 = False
        count1 = 0
        count2 = 0
        k1 = 0
        k2 = 0
        # Forward direction
        r, c = row + dr, col + dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if arr[r][c] == player and k1 == 0:
                count += 1
            elif arr[r][c] == 0 and k1 == 0:
                k1 = 1
                e1 = True
            elif arr[r][c] == player and k1 == 1:
                count1 += 1
                e1 = False
            elif arr[r][c] == 0 and k1 == 1:
                e1 = True
                break
            else:
                break
            r += dr
            c += dc
        # Reverse direction
        r, c = row - dr, col - dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if arr[r][c] == player and k2 == 0:
                count += 1
            elif arr[r][c] == 0 and k2 == 0:
                k2 = 1
                e2 = True
            elif arr[r][c] == player and k2 == 1:
                count2 += 1
                e2 = False
            elif arr[r][c] == 0 and k2 == 1:
                e2 = True
                break
            else:
                break
            r -= dr
            c -= dc
        
        
        if count >= 5:
            pattern[FIVE_IN_A_ROW] = 1
            return pattern
        
        if count >2 and player == -1:
            pass
        
        match (count1>0)+(count2>0):
            case 0:
                if count == 4 and e1 and e2:
                    pattern[OPEN_FOUR] += 1
                elif count == 4 and (e1 or e2):
                    pattern[CLOSED_FOUR] += 1
                elif count == 3 and e1 and e2:
                    pattern[OPEN_THREE] += 1
                elif count == 2 and (e1 or e2):
                    pattern[OPEN_TWO] += 1
            case 1:
                if count == 4:
                    if (count1 > 0 or e1) and (count2 > 0 or e2):
                        pattern[OPEN_FOUR] += 1
                    else:
                        pattern[CLOSED_FOUR] += 1
                elif count + count1 + count2  > 3:
                    if (count1==1 and e2) or (count2==1 and e1) or (e2 and e1):
                        pattern[FOUR_WITH_GAP] += 1
                    else:
                        pattern[CLOSED_FOUR] += 1
                elif count + count1 + count2 == 3 and e1 and e2:
                    pattern[OPEN_THREE_WITH_GAP] += 1
                elif count + count1 + count2 == 2 and (e1 or e2):
                    pattern[OPEN_TWO_WITH_GAP] += 1
            case 2:
                if count+count1 > 3 and count+count2 > 3:
                    pattern[OPEN_FOUR] += 1
                elif count+count1 > 3 or count+count2 > 3:
                    if (count1 > 2 and e1) or (count2 > 2 and e2) or (e1 and e2):
                        pattern[FOUR_WITH_GAP] += 1
                    else:
                        pattern[CLOSED_FOUR] += 1
                elif (count + count1 > 2 and e1) or (count + count2 > 2 and e2):
                    pattern[OPEN_THREE_WITH_GAP] += 1 
                else:
                    pattern[OPEN_TWO_WITH_GAP] += 1
        
    return pattern


class Gomoku:
    """
    Main Gomoku class that orchestrates:
    - UI rendering (with Tkinter)
    - Game logic (handling moves, undo, checking victory conditions)
    - AI interaction (through MCTS in a background thread)
    - Multi-language support for the interface
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
            "ai_turn_no_undo_message": "对手正在下棋时不能悔棋。",
            "black_label": "黑棋",
            "white_label": "白棋",
            "difficulty_labels": {
                "simple": "简单",
                "medium": "中等",
                "hard": "困难",
            },
            "about_title": "关于",
            "about_message": (
                "Gomoku (五子棋)\n\n"
                "AI 五子棋 – 这是一个由 ChatGPT o1 创建的 Python 项目，"
                "包含基于蒙特卡罗树搜索 (MCTS) 的 AI 和多语言支持。"
                "通过此项目，我们旨在研究高级推理模型如何应对复杂的现实世界任务。"
                "试试与 AI 进行一场策略性较量吧！\n\n"
                "GitHub 仓库："
            ),
            "about_close": "关闭",
            "hint_button": "提示",
            "no_hint_available": "目前没有可以显示的机会或威胁。"

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
            "ai_turn_no_undo_message": "Cannot undo during opponent's turn.",
            "black_label": "Black",
            "white_label": "White",
            "difficulty_labels": {
                "simple": "Easy",
                "medium": "Medium",
                "hard": "Hard",
            },
            "about_title": "About",
            "about_message": (
                "Gomoku (五子棋)\n\n"
                "AI Five-in-a-Row – This Python project, created with ChatGPT o1, features MCTS-based AI, multi-language support. "
                "Through this project, we aim to investigate how advanced reasoning models handle complex real world projects. "
                "Try and enjoy a strategic match against the AI.\n\n"
                "GitHub Repository:"
            ),
            "about_close": "Close",
            "hint_button": "Hints",
            "no_hint_available": "No opportunities or threats to show at the moment."
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
            "ai_turn_no_undo_message": "No se puede deshacer durante el turno del oponente.",
            "black_label": "Negro",
            "white_label": "Blanco",
            "difficulty_labels": {
                "simple": "Fácil",
                "medium": "Medio",
                "hard": "Difícil",
            },
            "about_title": "Acerca de",
            "about_message": (
                "Gomoku (五子棋)\n\n"
                "AI Cinco en Línea – Este proyecto de Python, creado con ChatGPT o1, presenta una IA basada en MCTS y soporte multilingüe. "
                "Con este proyecto, buscamos investigar cómo los modelos de razonamiento avanzado manejan tareas complejas del mundo real. "
                "Prueba y disfruta de un partido estratégico contra la IA.\n\n"
                "Repositorio de GitHub:"
            ),
            "about_close": "Cerrar",
            "hint_button": "Sugerencias",
            "no_hint_available": "No hay oportunidades ni amenazas para mostrar en este momento."
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
            "ai_turn_no_undo_message": "Impossible d'annuler pendant le tour de l'adversaire.",
            "black_label": "Noir",
            "white_label": "Blanc",
            "difficulty_labels": {
                "simple": "Facile",
                "medium": "Moyen",
                "hard": "Difficile",
            },
            "about_title": "À propos",
            "about_message": (
                "Gomoku (五子棋)\n\n"
                "AI Cinq-en-Range – Ce projet Python, créé avec ChatGPT o1, propose une IA basée sur MCTS et un support multilingue. "
                "À travers ce projet, nous cherchons à étudier comment les modèles de raisonnement avancé gèrent des tâches complexes dans le monde réel. "
                "Essayez et profitez d'un match stratégique contre l'IA.\n\n"
                "Dépôt GitHub:"
            ),
            "hint_button": "Conseils",
            "no_hint_available": "Aucune opportunité ou menace à afficher pour le moment.",
            "about_close": "Fermer"

        },
        "ja": {
            "title": "五目並べ",
            "reset_button": "再開",
            "undo_button": "取り消し",
            "difficulty_button": "難易度選択",
            "difficulty_window_title": "AIの難易度を選択",
            "difficulty_window_label": "AIの難易度を選択してください：",
            "ok_button": "OK",
            "current_player_prefix": "現在のプレイヤー: ",
            "black_time_prefix": "黒の現在の時間: ",
            "white_time_prefix": "白の現在の時間: ",
            "choose_side_title": "駒を選択",
            "choose_side_message": "先手（黒）でプレイしますか？",
            "game_over_title": "ゲーム終了",
            "game_over_win": "あなたの勝利です！",
            "game_over_lose": "AIの勝利です！",
            "no_undo_title": "情報",
            "no_undo_message": "取り消せる手がありません。",
            "game_end_no_undo_message": "ゲームは終了しています。取り消しはできません。",
            "ai_turn_no_undo_message": "相手のターン中に取り消しはできません。",
            "black_label": "黒",
            "white_label": "白",
            "difficulty_labels": {
                "simple": "簡単",
                "medium": "中級",
                "hard": "難しい",
            },
            "about_title": "概要",
            "about_message": (
                "五目並べ\n\n"
                "AI五目並べ - Pythonプロジェクト。MCTS（モンテカルロ木探索）を基盤としたAIと多言語サポートを特徴としています。"
                "戦略的な試合を楽しんでください！\n\n"
                "GitHubリポジトリ："
            ),
            "about_close": "閉じる",
            "hint_button": "ヒント",
            "no_hint_available": "現在表示できるチャンスや脅威はありません。"
        }
    }

    def __init__(self, root):
        """
        Constructor for the Gomoku class.
        Initializes the Tkinter window, game variables, and UI components.
        """
        try:
            pygame.mixer.init()  # Initialize the Pygame mixer for sound playback
            self.sound = pygame.mixer.Sound(resource_path("move_sound.mp3"))  # Load move sound
        except Exception as e:
            print(f"Error playing sound: {e}")

        self.root = root
        # Default UI language is set to English
        self.current_language = "en"
        # Default difficulty is set to "medium"
        self.current_difficulty = "medium"

        icon_path = "gomoku.png"  # Path to the game icon
        icon_image = ImageTk.PhotoImage(Image.open(icon_path))
        root.iconphoto(False, icon_image)  # Set the window icon

        # Set the window title according to the current language
        self.root.title(self.t("title"))
        self.root.config(bg=BG_COLOR)  # Set background color if BG_COLOR is defined

        # Calculate the total size of the canvas where the board will be drawn
        self.canvas_size = CELL_SIZE * (BOARD_SIZE - 1) + 2 * BOARD_PADDING

        # Create the Tkinter Canvas for drawing the board
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg='#E0C9A5')
        self.canvas.pack()

        # Bind the mouse click event to the click_event handler
        self.canvas.bind("<Button-1>", self.click_event)

        # Create a control frame at the bottom of the main window
        self.control_frame = tk.Frame(root, bg=BG_COLOR)
        self.control_frame.pack(fill="x", side="bottom", padx=5, pady=3)

        # First row: function buttons (Restart, Undo, Difficulty, About), centered
        self.button_frame = tk.Frame(self.control_frame, bg=BG_COLOR)
        self.button_frame.pack(side="top", pady=(0, 3))

        # Inner frame to hold the buttons
        self.button_frame_inner = tk.Frame(self.button_frame, bg=BG_COLOR)
        self.button_frame_inner.pack(anchor="center")

        # Restart button
        self.reset_button = tk.Button(
            self.button_frame_inner,
            text=self.t("reset_button"),
            command=self.reset_game,
            bg=BG_COLOR,
            activebackground="#D0D0D0",
            relief="groove"
        )
        self.reset_button.pack(side="left", padx=5)

        # Undo button
        self.undo_button = tk.Button(
            self.button_frame_inner,
            text=self.t("undo_button"),
            command=self.undo_move,
            bg=BG_COLOR,
            activebackground="#D0D0D0",
            relief="groove"
        )
        self.undo_button.pack(side="left", padx=5)

        # Difficulty button
        self.difficulty_button = tk.Button(
            self.button_frame_inner,
            text=self.get_difficulty_button_text(),
            command=self.select_difficulty,
            bg=BG_COLOR,
            activebackground="#D0D0D0",
            relief="groove"
        )
        self.difficulty_button.pack(side="left", padx=5)

        # List to store hint shape IDs, so we can clear them easily later
        self.hint_shapes = []

        # Hint button
        self.hint_button = tk.Button(
            self.button_frame_inner,
            text=self.t("hint_button"),
            command=self.show_hints,
            bg=BG_COLOR,
            relief="groove"
        )
        self.hint_button.pack(side="left", padx=5)

        # About button
        self.about_button = tk.Button(
            self.button_frame_inner,
            text=self.t("about_title"),
            command=self.show_about,
            bg=BG_COLOR,
            activebackground="#D0D0D0",
            relief="groove"
        )
        self.about_button.pack(side="left", padx=5)

        # Second row: language selection, centered
        self.language_frame = tk.Frame(self.control_frame, bg=BG_COLOR)
        self.language_frame.pack(side="top", pady=(0, 3))

        # Inner frame for radio buttons
        self.language_frame_inner = tk.Frame(self.language_frame, bg=BG_COLOR)
        self.language_frame_inner.pack(anchor="center")

        # Radio buttons for language selection
        self.selected_language = tk.StringVar(value=self.current_language)
        languages = [
            ("中文", "zh"), 
            ("English", "en"), 
            ("Español", "es"), 
            ("Français", "fr"), 
            ("日本語", "ja")
        ]
        for text, code in languages:
            rb = tk.Radiobutton(
                self.language_frame_inner,
                text=text,
                value=code,
                variable=self.selected_language,
                command=lambda c=code: self.set_language(c),
                bg=BG_COLOR,
                activebackground="#E0E0E0",
                selectcolor="#D0D0D0"
            )
            rb.pack(side="left", padx=5)
        
        # Create a status frame for labeling current player, timers, etc.
        self.status_frame = tk.Frame(root, bg=BG_COLOR)
        self.status_frame.pack(pady=2)

        # Label to show current player (e.g., "Current Player: Black")
        self.current_player_label = tk.Label(
            self.status_frame,
            text=f"{self.t('current_player_prefix')}{self.t('black_label')}",
            font=("Arial", 12), bg=BG_COLOR
        )
        self.current_player_label.grid(row=0, column=0, padx=10)

        # Label to show player's timer (when playing black)
        self.player_timer_label = tk.Label(
            self.status_frame,
            text=f"{self.t('black_time_prefix')}00.00",
            font=("Arial", 12), bg=BG_COLOR
        )
        self.player_timer_label.grid(row=0, column=1, padx=10)

        # Label to show AI's timer (when AI is white)
        self.ai_timer_label = tk.Label(
            self.status_frame,
            text=f"{self.t('white_time_prefix')}00.00",
            font=("Arial", 12), bg=BG_COLOR
        )
        self.ai_timer_label.grid(row=0, column=2, padx=10)

        # Variables to measure the time for each side
        self.player_start_time = None
        self.ai_start_time = None

        # 15x15 board data structure: each cell can be 'black', 'white', or '' (empty)
        self.board = [array('b', [0] * BOARD_SIZE) for _ in range(BOARD_SIZE)]

        # Game over flag
        self.game_over = False
        # Current turn: 'black' or 'white'
        self.current_turn = 1
        # Move history for undo functionality
        self.move_history = []
        # Highlight shape ID for the last move
        self.highlight = None

        # A thread-safe queue for receiving AI moves
        self.ai_move_queue = queue.Queue()

        # Schedule a regular check for AI moves in the main thread
        self.root.after(100, self.process_ai_move)

        # Draw the empty board (lines, star points, etc.)
        self.draw_board()

        # Set default difficulty (MCTS simulations, time limit) based on current_difficulty
        self.set_default_difficulty()

        # Ensure the main window is updated so geometry is correct, then center it
        self.root.update_idletasks()
        self.center_main_window()

        # Prompt the user to choose to play black or white
        self.choose_side()

    def t(self, key):
        """
        Return the text in the currently selected language for the given key.
        If the key is not found, return the key itself.
        """
        return self.translations[self.current_language].get(key, key)

    def get_difficulty_button_text(self):
        """
        Return the button text showing both the difficulty label and the translation.
        """
        diff_label = self.translations[self.current_language]["difficulty_labels"][self.current_difficulty]
        return f"{self.t('difficulty_button')} ({diff_label})"

    def show_hints(self):
        """
        Show the next moves' opportunities (green circles) and threats (red markers).
        - Uses get_hints(...) to detect patterns for the current player and the opponent.
        - Draws markers on the canvas to indicate these hints.
        """
        # If it's not the player's turn, don't show hints
        if self.current_turn != self.player:
            return

        # Clear previous hint markers first
        self.hide_hints()

        # Retrieve pattern info for current player and opponent
        pattern_info = get_hints(self.board, self.current_turn, self.ai, self.player)
        pattern_info_me = pattern_info[0]
        pattern_info_opponent = pattern_info[1]
        pattern_info_score = pattern_info[2]
        

        '''
        # Draw score
        for ([r, c], value) in pattern_info_score:
            x1, y1 = self.board_to_pixel(r, c)
            shape_id = self.canvas.create_text(
                x1, y1,
                text=str(value),
                fill="blue",
                font=("Arial", 10, "bold"),
                tags="score"
            )
            self.hint_shapes.append(shape_id)

        # If no hints are available, show a message
        if not pattern_info_me and not pattern_info_opponent:
            messagebox.showinfo(self.t("hint_button"), self.t("no_hint_available"), parent=self.root)
            return

        '''


        # Draw green circles for opportunities
        for ([r, c], value) in pattern_info_me:
            x1, y1 = self.board_to_pixel(r, c)
            shape_id = self.canvas.create_oval(
                x1 - 15 * value, y1 - 15 * value,
                x1 + 15 * value, y1 + 15 * value,
                outline="#A3D9A5",
                width=2
            )
            self.hint_shapes.append(shape_id)

        # Draw red triangles for threats (opponent's opportunities)
        for ([r, c], value) in pattern_info_opponent:
            x1, y1 = self.board_to_pixel(r, c)
            triangle_id = self.canvas.create_polygon(
                x1, y1 - 17 * value,    # top vertex
                x1 - 16 * value, y1 + 10 * value,  # left bottom
                x1 + 16 * value, y1 + 10 * value,  # right bottom
                fill="",
                outline="#F5A3A3",
                width=2
            )
            self.hint_shapes.append(triangle_id)

    def hide_hints(self):
        """
        Remove all hint markers from the board.
        """
        for shape_id in self.hint_shapes:
            self.canvas.delete(shape_id)
        self.hint_shapes.clear()

    def set_language(self, lang_code):
        """
        Change the current UI language to lang_code and refresh UI texts.
        """
        self.current_language = lang_code
        self.update_ui_text()

    def update_ui_text(self):
        """
        Refresh the text of titles, buttons, labels, etc. to the currently selected language.
        """
        self.root.title(self.t("title"))
        self.reset_button.config(text=self.t("reset_button"))
        self.undo_button.config(text=self.t("undo_button"))
        self.about_button.config(text=self.t("about_title"))
        self.difficulty_button.config(text=self.get_difficulty_button_text())
        self.hint_button.config(text=self.t("hint_button"))

        current_player = self.t("black_label") if self.current_turn == 'black' else self.t("white_label")
        self.current_player_label.config(text=f"{self.t('current_player_prefix')}{current_player}")

        # If timers haven't started, display default time "00.00"
        if self.player_start_time is None:
            self.player_timer_label.config(text=f"{self.t('black_time_prefix')}00.00")
        if self.ai_start_time is None:
            self.ai_timer_label.config(text=f"{self.t('white_time_prefix')}00.00")

    def center_main_window(self):
        """
        Place the main Tkinter window at the center of the screen.
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
        Set the MCTS parameters (simulations, time limit) based on the current difficulty.
        """
        self.mcts_simulations = DIFFICULTY_LEVELS[self.current_difficulty]['simulations']
        self.time_limit = DIFFICULTY_LEVELS[self.current_difficulty]['time_limit']

    def select_difficulty(self):
        """
        Open a popup window to let the user select AI difficulty.
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
        Callback for the difficulty selection. Updates current difficulty and closes the popup.
        """
        difficulty = self.selected_difficulty.get()
        self.current_difficulty = difficulty
        self.set_default_difficulty()
        self.difficulty_window.destroy()
        self.difficulty_button.config(text=self.get_difficulty_button_text())

    def choose_side(self):
        """
        Ask the user: "Do you want to play first (Black)?" (Yes/No)
        If yes => player is black, AI is white
        If no => player is white, AI is black
        If AI goes first, AI will make an initial move (usually center).
        """
        self.root.update_idletasks()
        self.center_main_window()

        answer = messagebox.askquestion(
            self.t("choose_side_title"),
            self.t("choose_side_message"),
            parent=self.root
        )
        if answer == 'yes':
            self.player = 1
            self.ai = -1
            self.current_turn = self.player
            self.update_status()
            self.start_timer()
        else:
            self.player = -1
            self.ai = 1
            self.current_turn = self.ai
            self.update_status()
            self.start_timer()
            # AI performs the first move if it's black (often center)
            self.perform_ai_move(BOARD_SIZE // 2, BOARD_SIZE // 2)

    def reset_game(self):
        """
        Reset the board state and UI, then prompt the user which side to play.
        """
        self.board = [array('b', [0] * BOARD_SIZE) for _ in range(BOARD_SIZE)]
        self.canvas.delete("all")
        self.draw_board()
        self.game_over = False
        self.current_turn = 1
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
        Draw the 15x15 board with horizontal/vertical lines and star points.
        """
        # Draw horizontal and vertical lines
        for i in range(BOARD_SIZE):
            # Horizontal line
            self.canvas.create_line(
                BOARD_PADDING,
                BOARD_PADDING + i * CELL_SIZE,
                BOARD_PADDING + (BOARD_SIZE - 1) * CELL_SIZE,
                BOARD_PADDING + i * CELL_SIZE
            )
            # Vertical line
            self.canvas.create_line(
                BOARD_PADDING + i * CELL_SIZE,
                BOARD_PADDING,
                BOARD_PADDING + i * CELL_SIZE,
                BOARD_PADDING + (BOARD_SIZE - 1) * CELL_SIZE
            )
        # Draw star points (3-3, 3-7, 3-11, etc.)
        star_points = [3, BOARD_SIZE // 2, BOARD_SIZE - 4]
        for i in star_points:
            for j in star_points:
                x = BOARD_PADDING + i * CELL_SIZE
                y = BOARD_PADDING + j * CELL_SIZE
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='black')

    def show_about(self):
        """
        Show a popup window with 'About' information and a GitHub link.
        """
        title = self.t("about_title")
        message = self.t("about_message")
        close_button_text = self.t("about_close")

        about_window = tk.Toplevel(self.root)
        about_window.title(title)
        about_window.transient(self.root)
        about_window.grab_set()

        tk.Label(
            about_window,
            text=message,
            justify="left",
            wraplength=300,
            font=("Arial", 10)
        ).pack(pady=10, padx=15)

        # Clickable GitHub link
        github_link = tk.Label(
            about_window,
            text="https://github.com/cooltesttry/Gomoku-O1",
            fg="blue",
            cursor="hand2",
            font=("Arial", 10, "underline")
        )
        github_link.pack(pady=(0, 15))
        github_link.bind("<Button-1>", lambda e: self.open_link("https://github.com/cooltesttry/Gomoku-O1"))

        close_button = tk.Button(
            about_window,
            text=" " + close_button_text + " ",
            command=about_window.destroy,
            bg="#ADD8E6",
            activebackground="#D0D0D0",
            font=("Arial", 10),
            relief="groove"
        )
        close_button.pack(pady=(5, 15))
        self.center_window(about_window, self.root)

    def open_link(self, url):
        """
        Open the given URL in the default web browser.
        """
        import webbrowser
        webbrowser.open(url)

    def click_event(self, event):
        """
        Handle mouse click events on the board. 
        If it's the player's turn, place the stone if valid, check for win, switch turn to AI.
        """
        if self.game_over:
            return
        if self.current_turn != self.player:
            return

        # Hide existing hints once a move is made
        self.hide_hints()

        x = event.x
        y = event.y
        row, col = self.get_nearest_point(x, y)
        # If the click is out of range or cell is occupied, ignore
        if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
            return
        if self.board[row][col] != 0:
            return

        # Place the stone for the player
        self.play_move_sound()
        self.place_stone(row, col, self.player)
        self.move_history.append((self.player, row, col))
        self.stop_timer()

        # Check if the player has won
        if check_win(self.board, (row, col), self.player):
            messagebox.showinfo(self.t("game_over_title"), self.t("game_over_win"), parent=self.root)
            self.game_over = True
            return
        
        start = time.time()
        '''
        for _ in range(100000):
            check_win(self.board, (row, col), 1)
        end = time.time()
        print("1 耗时:", end - start)

        for _ in range(100000):
            self.check_win(row, col, 1)
        end = time.time()
        print("1 耗时:", end - start)
        '''
        # Switch turn to AI
        self.current_turn = self.ai
        self.update_status()
        self.highlight_last_move()
        self.start_timer()

        # Start a thread for AI computations (no GUI calls in that thread)
        self.root.after(100, lambda: threading.Thread(target=self.ai_move_thread, daemon=True).start())

    def ai_move_thread(self):
        """
        Run the AI logic (MCTS) in a background thread, then put the resulting move into a queue.
        """
        move = self.find_best_move()
        if move:
            self.ai_move_queue.put(move)

    def process_ai_move(self):
        """
        Repeatedly check if there is an AI move in the queue.
        If so, execute it in the main thread (safe for Tkinter).
        """
        try:
            while True:
                move = self.ai_move_queue.get_nowait()
                self.perform_ai_move(move[0], move[1])
        except queue.Empty:
            pass

        # Schedule the next call
        self.root.after(100, self.process_ai_move)

    def play_move_sound(self):
        """
        Play a stone placement sound if available.
        """
        try:
            self.sound.play()
        except Exception as e:
            print(f"Error playing sound: {e}")

    def perform_ai_move(self, row, col):
        """
        Execute the AI's move on the board, check for a win, then switch back to player.
        """
        if self.game_over:
            return

        # Place the AI's stone
        self.play_move_sound()
        self.place_stone(row, col, self.ai)
        self.move_history.append((self.ai, row, col))
        self.stop_timer()

        # Check if AI wins
        if check_win(self.board, (row, col), self.ai):
            messagebox.showinfo(self.t("game_over_title"), self.t("game_over_lose"), parent=self.root)
            self.game_over = True
            return

        # Switch turn to the player
        self.current_turn = self.player
        self.update_status()
        self.highlight_last_move()
        self.start_timer()

    def get_nearest_point(self, x, y):
        """
        Convert the clicked canvas coordinates (x, y) to the nearest board cell (row, col).
        If the click is not close enough to the grid center, return (-1, -1).
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
        Update the board data with the player's stone, then draw it on the canvas.
        """
        self.board[row][col] = player
        x, y = self.board_to_pixel(row, col)
        self.draw_3d_stone(x, y, 1 if player == 1 else -1)

    def board_to_pixel(self, row, col):
        """
        Convert board coordinates (row, col) to pixel coordinates (x, y) on the canvas.
        """
        x = BOARD_PADDING + col * CELL_SIZE
        y = BOARD_PADDING + row * CELL_SIZE
        return (x, y)

    def draw_3d_stone(self, x, y, color):
        """
        Draw a stone with a slight 3D effect on the canvas.
        'color' should be 'black' or 'white'.
        """
        # Draw the main stone circle
        self.canvas.create_oval(
            x - STONE_RADIUS, y - STONE_RADIUS,
            x + STONE_RADIUS, y + STONE_RADIUS,
            fill='black' if color == 1 else '#EEEEEE',
            outline='',
            tags="stone"
        )
        # Highlight region for a 3D effect
        if color == 1:
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
        # Shadow region for a 3D effect
        shadow_color = '#555555' if color == 1 else '#E0E0E0'
        self.canvas.create_oval(
            x + STONE_RADIUS - 10, y + STONE_RADIUS - 10,
            x + STONE_RADIUS - 5, y + STONE_RADIUS - 5,
            fill=shadow_color,
            outline='',
            tags="stone"
        )


    def find_best_move(self):
        """
        Perform the MCTS search to find the best move for the AI.
        Returns the (row, col) of the best move.
        """
        return mcts_search(self.board, self.ai, self.player, self.mcts_simulations, self.time_limit)

    def undo_move(self):
        """
        Undo the last two moves (AI + player) if possible, as long as the game isn't over and it's player's turn.
        """
        if not self.move_history:
            messagebox.showinfo(self.t("no_undo_title"), self.t("no_undo_message"), parent=self.root)
            return
        if self.game_over:
            messagebox.showinfo(self.t("no_undo_title"), self.t("game_end_no_undo_message"), parent=self.root)
            return
        if self.current_turn != self.player:
            messagebox.showinfo(self.t("no_undo_title"), self.t("ai_turn_no_undo_message"), parent=self.root)
            return

        # Remove the last move from history
        last_player, row, col = self.move_history.pop()
        self.board[row][col] = 0
        self.redraw_board()
        self.highlight_last_move()

        # If the last move was AI's move, also remove the player's previous move
        if last_player == self.ai and self.move_history:
            last_player, row, col = self.move_history.pop()
            self.board[row][col] = 0
            self.redraw_board()
            self.highlight_last_move()

        self.current_turn = self.player
        self.update_status()
        self.stop_timer()
        self.start_timer()

    def redraw_board(self):
        """
        Clear the stones from the canvas and redraw them based on the self.board data.
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
        Draw a red circle (highlight) around the last placed stone.
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
        Update the status label to display the current player's turn.
        """
        current_player = self.t("black_label") if self.current_turn == 1 else self.t("white_label")
        self.current_player_label.config(text=f"{self.t('current_player_prefix')}{current_player}")

    def start_timer(self):
        """
        Start or resume the timer for the side whose turn it is (player or AI).
        """
        if self.current_turn == self.player:
            self.player_start_time = time.time()
            self.update_player_timer()
        else:
            self.ai_start_time = time.time()
            self.update_ai_timer()

    def stop_timer(self):
        """
        Stop the timer for the side whose turn just ended.
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
        Reset both player and AI timers to default "00.00".
        """
        self.player_start_time = None
        self.ai_start_time = None
        self.player_timer_label.config(text=f"{self.t('black_time_prefix')}00.00")
        self.ai_timer_label.config(text=f"{self.t('white_time_prefix')}00.00")

    def update_player_timer(self):
        """
        Continuously update the player's timer if it is running.
        """
        if self.player_start_time:
            elapsed = time.time() - self.player_start_time
            self.player_timer_label.config(
                text=f"{self.t('black_time_prefix')}{self.format_time(elapsed)}"
            )
            self.root.after(100, self.update_player_timer)

    def update_ai_timer(self):
        """
        Continuously update the AI's timer if it is running.
        """
        if self.ai_start_time:
            elapsed = time.time() - self.ai_start_time
            self.ai_timer_label.config(
                text=f"{self.t('white_time_prefix')}{self.format_time(elapsed)}"
            )
            self.root.after(100, self.update_ai_timer)

    def format_time(self, seconds):
        """
        Convert a time in seconds to a string "SS.mm" (seconds + 2 decimal places).
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
    Main entry point for the Monte Carlo Tree Search. Returns the best move (row, col).
    :param board: A 15x15 list of lists representing the board state
    :param ai_player: 'black' or 'white'
    :param human_player: 'black' or 'white'
    :param simulations: Number of MCTS simulations
    :param time_limit: Time limit for the MCTS (in seconds)
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

    # Use multiprocessing for parallel MCTS simulations
    with Pool(processes=cpu_count()) as pool:
        # Map each simulation to the 'simulate' function with the same root info
        results = pool.starmap(
            simulate,
            [(root, ai_player, human_player, end_time) for _ in range(simulations)]
        )

    # Collect move statistics
    move_scores = {}
    for move in results:
        if move is not None:
            move_scores[move] = move_scores.get(move, 0) + 1

    # Get all possible moves
    possible_moves = get_possible_moves(board)

    
    # Check for forced moves (e.g. immediate winning or blocking)
    force_moves , scores = get_forced_moves(board, possible_moves, ai_player)
    if force_moves:
        # If there are forced moves and no moves in move_scores, pick one
        if not move_scores:
            return random.choice(force_moves)
        # Otherwise pick the forced move with highest frequency
        force_scores = {}
        for move in force_moves:
            force_scores[move] = move_scores.get(move, 0)
            best_move = max(force_scores, key=force_scores.get)
        return best_move

    # If MCTS did not yield any expansions (very rare), pick a random move
    if not move_scores:
        return random.choice(possible_moves)
    
    # Otherwise, choose the move that was most frequent in the simulations
    best_move = max(move_scores, key=move_scores.get)
    return best_move


class MCTSNode:
    """
    A node representing a state in the MCTS tree.
    Holds board data, player info, and statistics like wins/visits.
    """
    def __init__(self, board, player, ai_player, human_player, move=None, parent=None):
        self.board = board                # 15x15 board state
        self.player = player              # Which player to move at this node
        self.ai_player = ai_player
        self.human_player = human_player
        self.move = move                  # The move (row, col) that led to this node
        self.parent = parent
        self.children = {}                # A dictionary of move -> MCTSNode
        self.wins = 0                     # Accumulated wins (for AI) during backprop
        self.visits = 0
        self.goodmove = get_good_moves(self.board,self.player)                  # Number of visits for this node
        self.movelen = len(self.goodmove)

    def is_fully_expanded(self):
        """
        Return True if all possible moves from this board state have been expanded.
        """
        return len(self.children) == self.movelen

    def best_child(self, c_param=1.414):
        """
        Select the best child node using UCB (Upper Confidence Bound):
        UCB = (child.wins / child.visits) + c_param * sqrt( (ln(self.visits)) / child.visits )
        """
        best_score = -INF
        best_move = None
        for move, child in self.children.items():
            if child.visits == 0:
                # If child is unvisited, return it immediately
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
    Execute one simulation of MCTS:
    1. SELECTION: Move down the tree using best_child() until a non-full node is found
    2. EXPANSION: Create a new child node with a random feasible move
    3. SIMULATION (Playout): Play out random moves until a result or time is up
    4. BACKPROPAGATION: Update nodes with the result of the simulation
    Returns the move that was expanded in this simulation (None if none).
    """
    current_node = node
    board = copy.deepcopy(node.board)
    player = current_node.player

    # 1) SELECTION
    while current_node.is_fully_expanded() and current_node.children:
        current_node = current_node.best_child()
        if current_node and current_node.move:
            board[current_node.move[0]][current_node.move[1]] = current_node.player
            # Switch player
            player = ai_player if current_node.player == human_player else human_player
        else:
            break

    # 2) EXPANSION
    possible_moves = current_node.goodmove
    if possible_moves and current_node:
        move = random.choice(possible_moves)

        board[move[0]][move[1]] = player
        if move not in current_node.children:

            child_node = MCTSNode(
                board=copy.deepcopy(board),
                player=ai_player if player == human_player else human_player,
                ai_player=ai_player,
                human_player=human_player,
                move=move,
                parent=current_node
            )
            current_node.children[move] = child_node
        else:
            child_node = current_node.children[move]
        player = ai_player if player == human_player else human_player
    else:
        move = None

    # 3) SIMULATION (random playout) until winner or time
    winner = None
    while True:
        # Check if the last move caused a win for AI/human
        if move is not None and check_win(board, move, ai_player):
            winner = ai_player
            break
        elif move is not None and check_win(board, move, human_player):
            winner = human_player
            break

        # If no more moves, it's a draw
        possible_moves = get_possible_moves(board)
        if not possible_moves:
            break

        # Choose a random move
        move = random.choice(possible_moves)
        board[move[0]][move[1]] = player

        # Check winner
        if check_win(board, move, player):
            winner = player
            break

        # Switch player
        player = ai_player if player == human_player else human_player

        # Time check
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

def get_good_moves(board, player):
    moves=get_possible_moves(board)
    if moves:
        forced_moves, scores = get_forced_moves(board, moves, player, True)
        if forced_moves:
            moves = forced_moves
        moves.sort(key=lambda x: scores[x])
        filtered_moves = [move for move in moves if scores[move] > 0]
    if filtered_moves:
        return filtered_moves
    return moves

def check_win(board, move, player):
    """
    Check if the 'player' has won by placing a stone at 'move' (row, col).
    Used in MCTS simulations (no GUI).
    """
    if move is None:
        return False
    row, col = move
    for dr, dc in DIRECTIONS:
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
    Return all 'reasonable' empty positions (within 2 cells of an existing stone).
    If the board is empty, return the center position (start move).
    """
    moves = set()
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] != 0:
                # For each occupied cell, add empty cells in a 2-cell radius to 'moves'
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        r, c = row + dr, col + dc
                        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == 0:
                            moves.add((r, c))
    if not moves:
        return [(BOARD_SIZE // 2, BOARD_SIZE // 2)]
    return list(moves)


def get_hints(board, player, ai_player, human_player):
    """
    Analyze the board to find 'hints' for the current player:
    - Opportunities for the current player
    - Threats from the opponent
    The function returns a list [player_hints, opponent_hints].
    Each item is a list of tuples ([row, col], value), where 'value' scales the marker size.
    """
    player_hints = []
    opponent_hints = []
    scores = []
    possible_move = get_possible_moves(board)
    opponent = human_player if player == ai_player else ai_player
    for move in possible_move:
        r, c = move
        # Temporarily place player's stone
        
        patterns = check_pattern(board, r, c, player)
        play_score = patterns[FIVE_IN_A_ROW] * 1000 + patterns[OPEN_FOUR] * 100 + patterns[FOUR_WITH_GAP] * 50 + patterns[CLOSED_FOUR] * 20 + patterns[OPEN_THREE] * 10 + patterns[OPEN_THREE_WITH_GAP] * 5 + patterns[OPEN_TWO] * 2 + patterns[OPEN_TWO_WITH_GAP]
        threats = patterns[FIVE_IN_A_ROW] + patterns[OPEN_FOUR] + patterns[FOUR_WITH_GAP] + patterns[OPEN_THREE] + patterns[OPEN_THREE_WITH_GAP]+ patterns[CLOSED_FOUR] 
        
        
        # If we detect strong patterns, record them as opportunities
        if threats > 0:
            # 'value' determines the size of the marker
            player_hints.append([move, 1 if patterns[FIVE_IN_A_ROW] + patterns[OPEN_FOUR] > 0 or threats > 1 else 0.6])
        

        # Temporarily place opponent's stone
        
        patterns = check_pattern(board, r, c, opponent)
        opp_score = patterns[FIVE_IN_A_ROW] * 1000 + patterns[OPEN_FOUR] * 100 + patterns[FOUR_WITH_GAP] * 50 + patterns[CLOSED_FOUR] * 20 + patterns[OPEN_THREE] * 10 + patterns[OPEN_THREE_WITH_GAP] * 5 + patterns[OPEN_TWO] * 2 + patterns[OPEN_TWO_WITH_GAP]

        # If the opponent has strong patterns, we consider them threats
        if sum (patterns[:6])> 1 or patterns[OPEN_FOUR] > 0 or patterns[FIVE_IN_A_ROW] > 0:
            opponent_hints.append([move, 1])
        elif patterns[OPEN_THREE] > 0:
            opponent_hints.append([move, 0.6])
            
        scores.append([move, play_score + opp_score])
        
    return [player_hints, opponent_hints, scores]


def get_forced_moves(board, amoves, player, calcscore=False):
    """
    Identify forced moves such as:
    - immediate win
    - blocking opponent's immediate win
    - creating or blocking four-in-a-row
    Returns a list of forced moves.
    """
    forced_moves = []
    me_moves = []
    me_4 = []
    me_3 = []
    o_5=[]
    o_4=[]
    o_3=[]
    o_threat=0
    scores = {}
    opponent = -player # Opponent's stone
    for move in amoves:
        r, c = move
        
        patterns = check_pattern(board, r, c, player)
        if calcscore:
            scores[move] = scores.get(move,0) + patterns[FIVE_IN_A_ROW] * 1000 + patterns[OPEN_FOUR] * 100 + patterns[FOUR_WITH_GAP] * 50 + patterns[CLOSED_FOUR] * 20 + patterns[OPEN_THREE] * 10 + patterns[OPEN_THREE_WITH_GAP] * 5 + patterns[OPEN_TWO] * 2 + patterns[OPEN_TWO_WITH_GAP]
        # If this move gives immediate five-in-a-row, return immediately
        if patterns[FIVE_IN_A_ROW] > 0:
        
            return [move,],scores
        else:
            # Check for open_four, threat_4, threat_3, etc.
            threat_4 = patterns[OPEN_FOUR] + patterns[FOUR_WITH_GAP] + patterns[CLOSED_FOUR]
            threat_3 = patterns[OPEN_THREE] + patterns[OPEN_THREE_WITH_GAP]
            if threat_4 > 0:
                me_4.append(move)
            if threat_3 > 0:
                me_3.append(move)
            if patterns[OPEN_FOUR] > 0:
                me_moves.append(move)
            elif threat_4 + threat_3 > 1:
                forced_moves.append(move)
      
        patterns = check_pattern(board, r, c, opponent)
        if calcscore:
            scores[move] = scores.get(move,0) + patterns[FIVE_IN_A_ROW] * 1000 + patterns[OPEN_FOUR] * 100 + patterns[FOUR_WITH_GAP] * 50 + patterns[CLOSED_FOUR] * 20 + patterns[OPEN_THREE] * 10 + patterns[OPEN_THREE_WITH_GAP] * 5 + patterns[OPEN_TWO] * 2 + patterns[OPEN_TWO_WITH_GAP]

        threat_4 = patterns[OPEN_FOUR] + patterns[FOUR_WITH_GAP] + patterns[CLOSED_FOUR]
        threat_3 = patterns[OPEN_THREE] + patterns[OPEN_THREE_WITH_GAP]
 
        if patterns[FIVE_IN_A_ROW] > 0:
            o_5.append(move)
            o_threat=5
        elif o_threat < 5:
            # If opponent can form open_four or multiple threats, add to forced moves
            if patterns[OPEN_FOUR] > 0 or (threat_4 + threat_3 > 1 and threat_4 > 0):
                o_4.append(move)
                o_threat=4
            elif threat_3 > 1 and o_threat<4:
                o_3.append(move)
                o_threat=3
    if o_threat==5:
        return o_5,scores
    elif me_moves:
        return me_moves,scores
    elif o_threat==4:
        return list(set(forced_moves + o_4 + me_4)),scores
    elif o_threat==3:
        return list(set(forced_moves + o_4 + o_3 + me_4 + me_3)),scores
    return list(set(forced_moves)), scores  # Remove duplicates


def main():
    """
    Application entry point.
    Create the Tkinter root window and start the Gomoku game loop.
    """
    root = tk.Tk()
    game = Gomoku(root)
    root.mainloop()


if __name__ == "__main__":
    freeze_support()  # For compatibility with multiprocessing on Windows
    main()