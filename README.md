# Gomoku-O1 (Five in a Row)

<img src="https://github.com/cooltesttry/Gomoku-O1/blob/main/screenshot.png" alt="Gomoku Example Board" width="300"/>

A **Python-based Gomoku (Five in a Row)** game with an MCTS-based AI. This project ALL done by ChatGPT o1, allowing you to play against an AI with selectable difficulty levels, switch languages on the fly, and experience additional features like undo, timers, and more. Support Windows, macOS, and Linux

### Download the Windows Executable

You can download the pre-built Windows executable. Simply click the link below. Run the file to start the Gomoku game without setup.:

**[Download Gomoku for Windows (EXE)](https://github.com/cooltesttry/Gomoku-O1/releases/download/Gomoku/Gomoku-O1.exe)**

**My Inner Journey**

This weekend, I decided to explore the limits of O1 by fully letting it lead a project. Over the course of 40 conversation rounds and about two hours, the result was a Gomoku program. It includes features like various AI difficulty levels supported by the Monte Carlo algorithm, multi-language support, cross-platform functionality, undo moves, timers, sound effects, and more. The entire interface and functionality were designed solely by O1 during our conversations. My role was simply to execute its instructions and provide feedback.

I watched as O1 planned, explored, debugged, and improved step by step. For instance, it initially used the minimax algorithm, but due to speed issues, it rewrote the logic with the Monte Carlo algorithm and multiprocessing. The interface and functionalities were incrementally enhanced and refined, with O1 simultaneously fixing its own bugs and seeking my feedback as user. It made mistakes but managed to detect and correct them. In some debugging conversations, I even sensed a kind of frustration from O1 over its errors. It also continually proposed new features for the program, and by the end, O1 was already discussing implementing online multiplayer. Unfortunately, my allocated O1 usage was nearly exhausted, so I couldn’t let it continue.

Through this process, I felt as though I was collaborating with an experienced human developer, yet the efficiency was beyond human. A workload that might take a regular programmer about a week was completed in just over two hours. I have complex feelings about this. While O1 is still far from AGI, it is very close to replacing basic programmers. In the future, humans may only need to serve as leaders and product managers. The code has been uploaded to GitHub, and even the README, description, and packaging were completed by O1—I merely handled the uploads.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Game Rules](#game-rules)
- [AI Difficulty](#ai-difficulty)
- [Multi-language Support](#multi-language-support)
- [Undo and Timers](#undo-and-timers)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

- **MCTS-Based AI**  
  Features a Monte Carlo Tree Search (MCTS) algorithm to determine the best move. Allows for different levels of difficulty.

- **Multiple Difficulty Levels**  
  Select from "Simple", "Medium", or "Hard" AI difficulty, each with different time limits and simulation counts.

- **Multi-language Support**  
  Built-in support for English (EN), Chinese (ZH), Spanish (ES), and French (FR). Switch languages in real-time from the UI.

- **Graphical User Interface**  
  Powered by Tkinter, providing an intuitive visual board with real-time updates.

- **Timers and Undo**  
  Each move (player or AI) is timed. You can also undo your moves (one undo action removes both the player's and AI's last moves).

- **Configurable Player Turn**  
  Choose whether to play first as Black or let the AI move first.

---

## Requirements

- **Python 3.10** 
- **Tkinter** (usually included by default in most Python distributions)

No additional third-party GUI libraries are required; the standard library `tkinter` is sufficient. However, the MCTS parallelization uses the [`multiprocessing`](https://docs.python.org/3/library/multiprocessing.html) module, which is also part of the Python standard library.

---

## Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/cooltesttry/Gomoku-O1.git
   cd Gomoku-O1
   ```

2. **(Optional) Create a Virtual Environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   # or
   venv\Scripts\activate     # On Windows
   ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

1. **Run the Gomoku Game**  
   ```bash
   python main.py
   ```

2. **Select Language**  
   - In the bottom-left corner of the main window, choose the language radio button (e.g., “中文”, “EN”, “ES”, “FR”).  
   - The interface text will update accordingly.

3. **Select AI Difficulty**  
   - In the bottom-right corner, click the “Difficulty” button to open a pop-up window.  
   - Choose **Simple**, **Medium**, or **Hard**.  
   - Confirm by clicking “OK”.

4. **Start the Game**  
   - Upon launching, a dialog box will ask if you want to move first (Black).  
   - Answer **Yes** to play Black first, or **No** to let the AI move first.

5. **Making a Move**  
   - Simply click on the board to place a stone on your turn.  
   - The AI will automatically take its turn afterwards.

6. **Undo a Move**  
   - Click the “Undo” button to reverse both your and the AI’s last moves.  
   - If no moves are available or the game has ended, you will see a message accordingly.

7. **Restart the Game**  
   - Use the “Restart” button at any time to reset the board and choose sides again.

---

## Game Rules

- **Board Size**: 15x15 grid.
- **Winning Condition**: First player to place **5 consecutive stones** in a row, column, or diagonal wins.
- **Turns**: Players alternate turns, placing one stone per turn.
- **Undo Feature**: Undoes the last move of each side (if the AI already moved).

---

## AI Difficulty

This project uses **Monte Carlo Tree Search (MCTS)** under different simulation limits and time constraints for each difficulty:

| Difficulty | Simulations | Time Limit (seconds) | Description                      |
|------------|------------:|---------------------:|----------------------------------|
| Simple     |         500 |                    2 | Faster but weaker AI.           |
| Medium     |        1000 |                    5 | Balanced level of AI thinking.  |
| Hard       |        3000 |                   12 | Deeper search, stronger AI.     |

---

## Multi-language Support

You can switch between English, Chinese, Spanish, and French at runtime. All UI text, including dialog messages, button labels, and status updates, will change immediately upon switching languages.

---

## Undo and Timers

- **Undo**:  
  - Each undo action removes the most recent moves of both the player and the AI (if the AI’s move occurred).  
  - Undo is disabled if no moves are made or if the game has ended.

- **Timers**:  
  - Each turn (player or AI) has its own step timer in seconds.  
  - When the turn switches, the previous player's timer stops, and the next player's timer starts.  
  - Displays **“Black Time”** and **“White Time”** with the duration in seconds and milliseconds.

---

## Project Structure

A possible structure (if the code is one file, you can list just that file):
```
.
├── main.py                  # Main entry point for the Gomoku game
├── README.md                # Project documentation
└── LICENSE                  # Open-source license file
```

**Key Components in `main.py`:**
- **`Gomoku` class**  
  Handles the main UI logic, board rendering, player interactions, timers, language switching, etc.

- **`mcts_search` function**  
  Orchestrates the MCTS simulations to pick the best move for the AI.

- **`simulate` function**  
  Handles the random playouts for each simulation, along with backpropagation.

- **`MCTSNode` class**  
  Represents a single node in the MCTS tree, storing board state, children nodes, and visit/win counts.

---

## Contributing

Contributions are welcome! If you’d like to help:

1. **Fork** the repository and **clone** it locally.
2. Create a new **feature branch** for your changes:
   ```bash
   git checkout -b feature-YourFeatureName
   ```
3. Make your changes or additions.
4. **Commit** and **push** to your branch.
5. Open a **Pull Request** describing your changes, and we’ll review it.

Please read our [CONTRIBUTING.md](CONTRIBUTING.md) (if available) for more details.

---

## License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## Contact

If you have any questions, suggestions, or feedback, feel free to open an [issue](https://github.com/cooltesttry/Gomoku-O1/issues)

We hope you enjoy playing Gomoku with our AI and welcome any contributions you might make!
