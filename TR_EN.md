## Part 1. Main Document.

### 1. Title and Basic Information.

• **Name:** Tetro Rally

• **Purpose:** Project No. 14. Product.

• **Project Phase:** Phase II.

• **Technology Stack:** Python (Pygame library).

• **Project Status:** Fully completed.

### 2. Project Overview.

**Tetro Rally** is an arcade-style Tetris game with competitive elements, developed in Python using the Pygame library.

The player competes against a built-in bot that automatically decides where to place pieces based on a heuristic evaluation of the game board.

Both boards (player and bot) are displayed simultaneously, and victory is determined by the "who loses first" principle — the player whose board fills up to the top loses the match.

This version of the project includes a main menu, help screen, Game Over screen, next-piece preview system, and best-score saving to a file.

The project is a fully functional version of the game with an extensive user interface, advanced game logic, and an AI-controlled opponent.

### 3. Clear Project Goals.

• Create a functional competitive version of Tetris with intuitive controls.

• Implement the core game mechanics: spawning, falling, rotating, moving, and clearing pieces when lines are completed.

• Implement an application state system (menu, help, game, game_over).

• Add a next-piece preview system for both the player and the bot.

• Implement a scoring system and save the best score to a JSON file.

• Ensure correct collision handling with the board boundaries and other pieces.

• Implement a bot opponent using a board evaluation algorithm.

• Implement a wall kick system for rotating pieces near the board boundaries.

• Ensure stable game performance at a fixed frame rate (60 FPS).

• Demonstrate an approach to developing game applications with a user interface and AI.

### 4. Project Components.

The project consists of a single executable file that includes all components:

• **tetro_rally.py** – the main script containing all game code, including game logic, interface, bot AI, and state management.

• **tetro_rally_data.json** – a file used to save the best score (created automatically after the first completed game).

### 5. Usage Instructions.

* **5.1. Launch:**

• Make sure the Pygame library is installed (pip install pygame).

• Run the script using Python (for example, from PyCharm).

* **5.2. Game Objective:**

• Complete horizontal lines using falling pieces to earn points.

• The game ends when either side (the player or the bot) can no longer place a new piece.

• If the player loses first, the bot wins; if the bot loses first, the player wins.

• The player's best score is saved to a file.

* **5.3. Controls:**

• **LEFT ARROW (←):** move the active piece left.

• **RIGHT ARROW (→):** move the active piece right.

• **DOWN ARROW (↓):** accelerate the falling speed of the active piece.

• **UP ARROW (↑):** rotate the active piece 90° clockwise.

• **SPACE:** instantly drop the piece to the lowest possible position.

• **ESC:** return to the main menu.

• **Mouse:** interact with buttons in the menu, help screen, and Game Over screen.

* **5.4. Interface:**

• Main menu with Play and Help buttons and the Best Score display.

• Help screen with descriptions of the controls and game rules.

• Two 10×20 game boards (player on the left, bot on the right).

• Top panel displaying:

• current player score (PLAYER)

• current bot score (BOT)

• VS label between the scores

• next piece for the player and bot (NEXT)

• Black cells with a gray grid – empty space.

• Colored cells – placed or falling pieces.

• Game Over screen with the match result and Play Again and Main Menu buttons.

* **5.5. Scoring System:**

• 1 line — 10 points

• 2 lines — 30 points

• 3 lines — 60 points

• 4 lines (Tetro) — 100 points

## Part 2. Technical Document.

### 1. Development Goals.

• The primary goal of the project was to create an extended competitive version of the classic Tetris game to strengthen Python programming skills and experience with the Pygame library.

• Additionally, the project focuses on learning how to build a user interface, manage application states, work with the file system (JSON), and implement simple artificial intelligence for a bot opponent.

• The tasks included working with matrices (game boards), handling user input, implementing collision detection, managing time intervals, and building the basic architecture of a game loop.

### 2. Technologies Used.

• **Programming Language:** Python

• **Graphics Library:** Pygame

• **Standard Libraries:** random (for piece generation), json (for save files), os (for checking whether the save file exists).

### 3. Project Architecture.

• The project is implemented as a monolithic application with elements of a finite-state machine.

• Main loop: while running:.

• The logic is divided into states:

• menu – main menu.

• help – help screen.

• game – gameplay.

• game_over – game over screen.

• Each frame performs event processing, state updates, game logic checks, and rendering.

• During gameplay, two independent subsystems operate simultaneously: player logic and bot logic.

### 4. Project Structure.

* **Initialization:** Pygame configuration, window creation, fonts, buttons, colors, and game parameters.

* **Global Variables:** player_board, bot_board, player_piece, bot_piece, player_next, bot_next, player_score, bot_score, best_score, state, winner, and others.

* **Game Loop:** the main loop responsible for state management and game logic.

* **Piece Class:**

• **init**(shape_id=None) – creates a piece (randomly or using a specified index).

• rotate() – rotates the piece 90°.

• cells() – returns a list of coordinates of all occupied cells of the piece.

* **Board Functions:**

• create_board() – creates an empty game board.

• valid_position(piece, board, dx, dy) – checks whether a piece can be placed at a given position.

• lock_piece(piece, board) – locks a piece onto the board.

• clear_lines(board) – removes completed lines.

• calculate_score(lines) – calculates the score for cleared lines.

• spawn_piece(next_piece) – spawns a new piece.

* **Bot AI Functions:**

• get_column_heights(board) – obtains the height of each column.

• count_holes(board) – counts "holes" (enclosed empty cells).

• board_score(board, cleared_lines) – calculates a heuristic evaluation of the board.

• simulate_move(piece, board, rotation, x_position) – simulates a move.

• bot_find_best_move(piece, board) – finds the best move.

• execute_bot_move() – executes the bot's move.

* **Rendering Functions:**

• draw_text(), draw_button(), draw_board(), draw_preview(), draw_top_panel(), draw_menu(), draw_help(), draw_game_over().

* **Game Management Functions:**

• reset_game() – resets the game.

• spawn_player(), spawn_bot() – spawns pieces.

• lock_player() – locks the player's piece.

• finish_game(who_wins) – ends the game.

• load_best_score(), save_best_score() – handles the best score.

### 5. Key System Components.

• **Game Board (board):** A two-dimensional list where each element contains either None (an empty cell) or the color of the piece (an occupied cell).

• **Pieces:** represented as matrices (shape), rotated using transposition and reversal (zip(*shape[::-1])), and selected randomly from the SHAPES list.

• **Next Piece System:** implemented using player_next and bot_next and displayed on the top panel.

• **Collision System:** checks board boundaries and occupied cells using valid_position().

• **Rotation System:** rotation around the central point using wall kick (X-axis offsets).

• **Bot AI System:** heuristic evaluation based on:

• number of cleared lines

• total tower height

• number of "holes"

• maximum height

• "bumpiness"

• **Best Score System:** JSON file tetro_rally_data.json.

### 6. User Interface Implementation.

• The interface is fully implemented using Pygame.

• Main elements: application window, menu buttons, two game boards, top panel, text elements, and the Game Over screen.

• Rendering is performed every frame using pygame.draw and pygame.font functions.

### 7. Development Process.

Development was carried out in several stages:

• creation of the basic game window

• implementation of the grid and game board

• addition of pieces and their movement

• implementation of collision detection

• addition of rotation with a wall kick system

• implementation of line clearing and score calculation

• addition of the menu and user interface

• addition of the next-piece system

• implementation of best-score saving in JSON

• addition of a second game board for the bot

• implementation of bot AI using heuristic evaluation

• addition of the Game Over screen and winner detection

### 8. Main Challenges and Solutions.

• **(1) Challenge:** correctly rotating pieces near walls and blocks.

**Solution:** a wall kick system was implemented to shift pieces when rotating.

• **(2) Challenge:** correctly clearing lines while preserving their colors.

**Solution:** both the cell state and cell color are copied during the process.

• **(3) Challenge:** implementing bot AI without instant piece placement.

**Solution:** the bot uses a bot_thinking delay and a flag to create a "thinking" effect, as well as a best-move search algorithm based on simulation.

• **(4) Challenge:** running two game boards simultaneously.

**Solution:** separate player_board and bot_board instances were created, along with independent piece objects for each board.

### 9. Current Project Limitations.

• No difficulty levels for the bot.

• The bot uses only one heuristic strategy (without machine learning).

• The code remains monolithic (without modular separation).

• No sound effects.

### 10. Potential Improvements and Future Development.

• Refactor the code (split it into modules and classes).

• Add difficulty levels and bot speed settings.

• Add sound effects.

• Add a leaderboard and statistics system.
