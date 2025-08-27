# Sejal Chess Engine and GUI

This project is a fully functional chess application featuring a custom-built chess engine and an intuitive graphical user interface (GUI). Developed in Python, it serves as both a challenging opponent for chess enthusiasts and a practical case study in artificial intelligence, search algorithms, and software design.

## Table of Contents
- [Philosophy](#philosophy)
- [Features](#features)
  - [Chess Engine](#chess-engine)
  - [Graphical User Interface (GUI)](#graphical-user-interface-gui)
- [The User Interface](#the-user-interface)
  - [Main Window](#main-window)
  - [Controls and Settings](#controls-and-settings)
- [How to Run](#how-to-run)
- [Project Structure](#project-structure)
- [Development Challenges & The Limits of Python](#development-challenges--the-limits-of-python)
- [Future Improvements](#future-improvements)

## Philosophy

The project was guided by a few core principles:

1.  **Modularity:** The chess engine (`engine.py`) is decoupled from the presentation layer (`gui.py`). The engine communicates using the standard Universal Chess Interface (UCI) protocol, allowing it to be used with any UCI-compatible GUI, not just the one provided.
2.  **Algorithmic Excellence:** The primary goal was to implement a strong chess-playing AI by exploring classic and modern computer science algorithms. The focus was on creating a robust search function with multiple layers of optimization to play competitively.
3.  **User Experience:** The GUI was designed to be clean, responsive, and user-friendly. It provides essential features without unnecessary clutter, making the experience of playing against the engine enjoyable.
4.  **Educational Value:** By using Python, a high-level and readable language, the project's source code is intended to be accessible to students and developers interested in game AI, serving as a clear example of complex algorithms in action.

## Features

### Chess Engine

The brain of the application is a UCI-compliant engine packed with sophisticated features to ensure strong gameplay.

*   **Alpha-Beta Pruning:** The core search algorithm, which dramatically reduces the number of nodes evaluated in the game tree compared to a standard minimax search.
*   **Iterative Deepening:** The engine searches to depth 1, then depth 2, and so on, allowing it to manage time effectively and stop at any point with the best move found so far.
*   **Transposition Table:** A large hash table stores previously evaluated positions. This saves immense computational effort by preventing the engine from analyzing the same position multiple times.
*   **Zobrist Hashing:** A highly efficient method for generating hash keys for board states, crucial for the performance of the transposition table.
*   **Quiescence Search:** To mitigate the "horizon effect," this specialized search extends the evaluation of volatile positions (like ongoing captures) to ensure the engine doesn't make tactical blunders based on a superficial analysis.
*   **Advanced Move Ordering:** The efficiency of alpha-beta pruning is highly dependent on the order in which moves are searched. We implement several heuristics:
    *   **Killer Moves:** Prioritizes moves that have previously caused a beta-cutoff.
    *   **History Heuristic:** Ranks moves based on how often they have been the best move in other parts of the search.
*   **Pruning Optimizations:**
    *   **Null Move Pruning:** A powerful technique where the engine gives the opponent an extra turn to see if its position is still dominant, allowing it to prune large sections of the search tree.
    *   **Late Move Reductions:** Reduces the search depth for moves that are ordered later, assuming they are less likely to be optimal.
*   **Aspiration Windows:** Narrows the search window for alpha and beta on subsequent searches, which can speed up the process if the score estimate is accurate.

### Graphical User Interface (GUI)

The GUI is built with PyQt5, providing a stable and feature-rich platform for gameplay.

*   **Interactive Chessboard:** A full 8x8 board with smooth, drag-and-drop piece movement.
*   **Player vs. Engine:** Play a full game of chess against the Sejal engine.
*   **Customizable Appearance:** Easily change the theme of the chessboard and the style of the pieces via the settings menu.
*   **FEN Support:** Load any valid chess position using a FEN (Forsyth-Edwards Notation) string.
*   **Visual Feedback:** The last move is highlighted, and legal moves for a selected piece are shown as subtle dots, making gameplay intuitive.
*   **Sound Effects:** Audio feedback for moves, captures, checks, and game-end events.

## The User Interface

### Main Window

The main application window is divided into two sections:
1.  **The Chessboard (Left):** This is the primary interaction area. You can move your pieces by clicking and dragging them to a valid square. The board will automatically flip to match your chosen color at the start of a new game.
2.  **The Side Panel (Right):** This panel contains:
    *   **Move List:** A complete, scrollable history of the game's moves in Standard Algebraic Notation (SAN).
    *   **Control Buttons:** A set of buttons to manage the game and application settings.

### Controls and Settings

*   **New Game:** Starts a new match from the standard starting position. A dialog will appear asking you to choose to play as White or Black.
*   **Load FEN:** Opens a dialog box where you can paste a FEN string. This is useful for setting up specific puzzles, analyzing famous games, or resuming a game from a known state.
*   **Settings:** Opens the settings window, which is divided into two tabs:
    *   **Appearance:** Contains dropdown menus to select your preferred **Piece Theme** and **Board Theme** from the available options.
    *   **Engine:** Allows you to set the **Engine Depth**, which controls how many moves ahead the engine thinks. A higher depth results in stronger play but requires more computation time.

## How to Run

1.  **Prerequisites:**
    *   Python 3.x

2.  **Create and Activate Virtual Environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    _On Windows, use `.venv\Scripts\activate`_

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application:**
    ```bash
    python gui.py
    ```
    The main window will appear, and a dialog will prompt you to start a new game by choosing your color.

5.  **Deactivate the Virtual Environment:**
    ```bash
    deactivate
    ```

## Project Structure

```
.
├── engine.py         # Core engine logic (search, UCI loop)
├── evaluation.py     # Evaluation function and piece-square tables
├── gui.py            # Main GUI application file (PyQt5)
├── main.py           # Stripped-down entry point for UCI communication
├── zobrist.py        # Zobrist hashing implementation
├── piece/            # Directory with SVG assets for piece themes
└── sound/            # Directory with MP3 sound effects
```

## Development Challenges & The Limits of Python

While Python offers excellent readability and a rich ecosystem, it presents significant challenges for performance-critical applications like chess engines.

*   **Performance Ceiling:** The primary limitation is speed. Python is an interpreted language and is orders of magnitude slower than compiled languages like C++, Rust, or C, which are the standard for competitive chess engines. The Global Interpreter Lock (GIL) also prevents true multi-threading for CPU-bound tasks like the search algorithm. A top-tier engine like Stockfish can evaluate tens of millions of nodes per second; a Python engine is typically limited to tens of thousands.

*   **Overcoming Performance Hurdles:** We addressed these limitations through several strategies:
    1.  **Algorithmic Efficiency:** The focus shifted from raw speed to algorithmic intelligence. Implementing advanced pruning techniques (Null Move, LMR) and an effective transposition table was crucial to cutting down the search space, ensuring the engine "thinks smarter, not harder."
    2.  **Incremental Updates:** Instead of re-calculating the board's Zobrist hash or evaluation score from scratch after each move, the engine uses incremental updates, which provides a massive performance boost.
    3.  **Leveraging Optimized Libraries:** The `python-chess` library is used for board representation and move generation. This library is highly optimized and provides a significant speed advantage over a pure Python implementation of the same logic.

Ultimately, while this engine cannot compete with the world's best, it demonstrates that a strong, feature-complete chess AI is achievable in Python and serves as an excellent platform for learning and experimentation.

## Future Improvements

*   **Improved Evaluation:** The evaluation function could be enhanced with more nuanced heuristics, such as piece mobility, passed pawn evaluation based on king distance, and king safety based on pawn shields and open files.
*   **Time Management:** Implement more sophisticated time controls to allow the engine to think longer in critical positions and respond faster in simple ones.
*   **Opening Book:** Integrate a curated opening book to improve the engine's play in the initial phase of the game and provide more variety.
*   **Endgame Tablebases:** For positions with a small number of pieces, using endgame tablebases would allow the engine to play perfectly.