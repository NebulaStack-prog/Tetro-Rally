import pygame
import random
import json
import os

pygame.init()

COLS = 10
ROWS = 20
CELL = 26
FIELD_WIDTH = COLS * CELL
FIELD_HEIGHT = ROWS * CELL
TOP_PANEL = 90
SCREEN_WIDTH = FIELD_WIDTH * 2 + 40
SCREEN_HEIGHT = FIELD_HEIGHT + TOP_PANEL + 20
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetro Rally")
clock = pygame.time.Clock()

BLACK = (8, 8, 12)
DARK = (18, 18, 25)
GRID = (45, 45, 55)
WHITE = (240, 240, 240)
GRAY = (130, 130, 140)
GREEN = (110, 180, 70)
GREEN_DARK = (60, 100, 40)
RED = (235, 70, 70)
BLUE = (70, 130, 240)
CYAN = (50, 210, 220)
YELLOW = (245, 220, 70)
ORANGE = (245, 145, 55)
PURPLE = (180, 80, 220)
PINK = (240, 80, 160)
PLAYER_COLOR = (110, 220, 120)
BOT_COLOR = (230, 90, 90)

font = pygame.font.Font(None, 25)
small_font = pygame.font.Font(None, 20)
title_font = pygame.font.Font(None, 60)
menu_font = pygame.font.Font(None, 34)
big_font = pygame.font.Font(None, 72)

SHAPES = [[[1, 1, 1, 1]], [[1, 1], [1, 1]], [[0, 1, 0], [1, 1, 1]], [[1, 0, 0], [1, 1, 1]], [[0, 0, 1], [1, 1, 1]], [[0, 1, 1], [1, 1, 0]], [[1, 1, 0], [0, 1, 1]]]
COLORS = [CYAN, YELLOW, PURPLE, ORANGE, BLUE, GREEN, RED]

MENU = "menu"
HELP = "help"
GAME = "game"
GAME_OVER = "game_over"

state = MENU
player_score = 0
bot_score = 0
best_score = 0
winner = None

SAVE_FILE = "tetro_rally_data.json"

def load_best_score():
    if not os.path.exists(SAVE_FILE):
        return 0
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("best_score", 0)
    except Exception:
        return 0

def save_best_score(value):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as file:
            json.dump({"best_score": value}, file)
    except Exception:
        pass

best_score = load_best_score()

class Piece:
    def __init__(self, shape_id=None):
        if shape_id is None:
            shape_id = random.randrange(len(SHAPES))
        self.shape_id = shape_id
        self.shape = [row[:] for row in SHAPES[shape_id]]
        self.color = COLORS[shape_id]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def cells(self):
        result = []
        for y, row in enumerate(self.shape):
            for x, value in enumerate(row):
                if value:
                    result.append((self.x + x, self.y + y))
        return result

def create_board():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]

player_board = create_board()
bot_board = create_board()

player_piece = None
player_next = None
bot_piece = None
bot_next = None

play_button = pygame.Rect(SCREEN_WIDTH // 2 - 90, 280, 180, 50)
help_button = pygame.Rect(SCREEN_WIDTH // 2 - 90, 350, 180, 50)
back_button = pygame.Rect(SCREEN_WIDTH // 2 - 90, 520, 180, 50)
restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 420, 200, 50)
menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 490, 200, 50)

player_drop_timer = 0
bot_drop_timer = 0
player_drop_delay = 550
bot_drop_delay = 420
bot_thinking = False

def valid_position(piece, board, dx=0, dy=0):
    for x, y in piece.cells():
        x += dx
        y += dy
        if x < 0 or x >= COLS:
            return False
        if y >= ROWS:
            return False
        if y >= 0 and board[y][x] is not None:
            return False
    return True

def lock_piece(piece, board):
    for x, y in piece.cells():
        if 0 <= y < ROWS and 0 <= x < COLS:
            board[y][x] = piece.color

def clear_lines(board):
    cleared = 0
    y = ROWS - 1
    while y >= 0:
        if all(board[y][x] is not None for x in range(COLS)):
            del board[y]
            board.insert(0, [None for _ in range(COLS)])
            cleared += 1
        else:
            y -= 1
    return cleared

def calculate_score(lines):
    if lines == 1:
        return 10
    if lines == 2:
        return 30
    if lines == 3:
        return 60
    if lines >= 4:
        return 100
    return 0

def spawn_piece(next_piece):
    if next_piece is None:
        piece = Piece()
    else:
        piece = next_piece
    next_piece = Piece()
    return piece, next_piece

def reset_game():
    global player_board, bot_board, player_piece, player_next, bot_piece, bot_next, player_score, bot_score, player_drop_timer, bot_drop_timer, winner, bot_thinking
    player_board = create_board()
    bot_board = create_board()
    player_piece, player_next = spawn_piece(None)
    bot_piece, bot_next = spawn_piece(None)
    player_score = 0
    bot_score = 0
    player_drop_timer = pygame.time.get_ticks()
    bot_drop_timer = pygame.time.get_ticks()
    winner = None
    bot_thinking = False

def get_column_heights(board):
    heights = []
    for x in range(COLS):
        height = 0
        for y in range(ROWS):
            if board[y][x] is not None:
                height = ROWS - y
                break
        heights.append(height)
    return heights

def count_holes(board):
    holes = 0
    for x in range(COLS):
        block_found = False
        for y in range(ROWS):
            if board[y][x] is not None:
                block_found = True
            elif block_found:
                holes += 1
    return holes

def board_score(board, cleared_lines):
    heights = get_column_heights(board)
    total_height = sum(heights)
    max_height = max(heights)
    holes = count_holes(board)
    bumpiness = 0
    for i in range(len(heights) - 1):
        bumpiness += abs(heights[i] - heights[i + 1])
    score = 0
    score += cleared_lines * 100
    score -= total_height * 1.2
    score -= holes * 7
    score -= max_height * 2
    score -= bumpiness * 1.5
    return score

def simulate_move(piece, board, rotation, x_position):
    test_piece = Piece(piece.shape_id)
    test_piece.shape = [row[:] for row in piece.shape]
    for _ in range(rotation):
        test_piece.rotate()
    test_piece.x = x_position
    test_piece.y = 0
    if not valid_position(test_piece, board):
        return None
    while valid_position(test_piece, board, dy=1):
        test_piece.y += 1
    test_board = [row[:] for row in board]
    lock_piece(test_piece, test_board)
    lines = clear_lines(test_board)
    score = board_score(test_board, lines)
    return score, rotation, x_position

def bot_find_best_move(piece, board):
    best = None
    for rotation in range(4):
        test_piece = Piece(piece.shape_id)
        test_piece.shape = [row[:] for row in piece.shape]
        for _ in range(rotation):
            test_piece.rotate()
        width = len(test_piece.shape[0])
        for x in range(-2, COLS - width + 2):
            result = simulate_move(piece, board, rotation, x)
            if result is None:
                continue
            score, r, xpos = result
            if best is None or score > best[0]:
                best = (score, r, xpos)
    return best

def execute_bot_move():
    global bot_piece, bot_score
    if bot_piece is None:
        return
    move = bot_find_best_move(bot_piece, bot_board)
    if move is None:
        return
    _, rotation, target_x = move
    for _ in range(rotation):
        bot_piece.rotate()
    bot_piece.x = target_x
    while valid_position(bot_piece, bot_board, dy=1):
        bot_piece.y += 1
    lock_piece(bot_piece, bot_board)
    lines = clear_lines(bot_board)
    bot_score += calculate_score(lines)

def draw_text(text, font_obj, color, center):
    surface = font_obj.render(text, True, color)
    rect = surface.get_rect(center=center)
    screen.blit(surface, rect)

def draw_button(rect, text):
    pygame.draw.rect(screen, GREEN_DARK, rect)
    pygame.draw.rect(screen, GREEN, rect, 2)
    draw_text(text, font, WHITE, rect.center)

def draw_board(board, offset_x, current_piece=None, label=None):
    field_rect = pygame.Rect(offset_x, TOP_PANEL, FIELD_WIDTH, FIELD_HEIGHT)
    pygame.draw.rect(screen, BLACK, field_rect)
    pygame.draw.rect(screen, GRAY, field_rect, 2)
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(offset_x + x * CELL, TOP_PANEL + y * CELL, CELL, CELL)
            pygame.draw.rect(screen, GRID, rect, 1)
            if board[y][x] is not None:
                pygame.draw.rect(screen, board[y][x], rect.inflate(-2, -2))
                pygame.draw.rect(screen, WHITE, rect.inflate(-4, -4), 1)
    if current_piece:
        for x, y in current_piece.cells():
            if y < 0:
                continue
            rect = pygame.Rect(offset_x + x * CELL, TOP_PANEL + y * CELL, CELL, CELL)
            pygame.draw.rect(screen, current_piece.color, rect.inflate(-2, -2))
            pygame.draw.rect(screen, WHITE, rect.inflate(-4, -4), 1)
    if label:
        draw_text(label, font, WHITE, (offset_x + FIELD_WIDTH // 2, TOP_PANEL - 25))

def draw_preview(piece, x, y):
    if piece is None:
        return
    size = 16
    width = len(piece.shape[0])
    height = len(piece.shape)
    start_x = x - width * size // 2
    start_y = y - height * size // 2
    for py, row in enumerate(piece.shape):
        for px, value in enumerate(row):
            if value:
                rect = pygame.Rect(start_x + px * size, start_y + py * size, size - 2, size - 2)
                pygame.draw.rect(screen, piece.color, rect)

def draw_top_panel():
    pygame.draw.rect(screen, DARK, (0, 0, SCREEN_WIDTH, TOP_PANEL))
    pygame.draw.line(screen, GRID, (0, TOP_PANEL - 1), (SCREEN_WIDTH, TOP_PANEL - 1))
    draw_text(f"PLAYER  {player_score}", font, PLAYER_COLOR, (FIELD_WIDTH // 2, 20))
    draw_text(f"BOT  {bot_score}", font, BOT_COLOR, (FIELD_WIDTH + 40 + FIELD_WIDTH // 2, 20))
    draw_text("VS", small_font, WHITE, (SCREEN_WIDTH // 2, 18))
    draw_text("NEXT", small_font, GRAY, (FIELD_WIDTH - 45, 58))
    draw_text("NEXT", small_font, GRAY, (FIELD_WIDTH * 2 - 25, 58))
    draw_preview(player_next, FIELD_WIDTH + 10, 58)
    draw_preview(bot_next, FIELD_WIDTH + 40 + FIELD_WIDTH - 10, 58)

def draw_menu():
    screen.fill(BLACK)
    draw_text("TETRO RALLY", title_font, GREEN, (SCREEN_WIDTH // 2, 150))
    draw_text("TETRIS VS BOT", small_font, GRAY, (SCREEN_WIDTH // 2, 200))
    draw_button(play_button, "PLAY")
    draw_button(help_button, "HELP")
    draw_text(f"BEST SCORE: {best_score}", small_font, YELLOW, (SCREEN_WIDTH // 2, 440))

def draw_help():
    screen.fill(BLACK)
    draw_text("HOW TO PLAY", title_font, GREEN, (SCREEN_WIDTH // 2, 90))
    instructions = ["LEFT / RIGHT - MOVE", "UP - ROTATE", "DOWN - FAST DROP", "ESC - MENU", "", "CLEAR LINES TO SCORE POINTS", "THE BOT PLAYS AUTOMATICALLY", "", "FIRST PLAYER TO LOSE THE FIELD", "LOSES THE MATCH"]
    y = 170
    for line in instructions:
        draw_text(line, small_font, WHITE, (SCREEN_WIDTH // 2, y))
        y += 30
    draw_button(back_button, "BACK")

def draw_game_over():
    screen.fill(BLACK)
    if winner == "player":
        title = "YOU WIN!"
        color = PLAYER_COLOR
    elif winner == "bot":
        title = "BOT WINS"
        color = BOT_COLOR
    else:
        title = "DRAW"
        color = YELLOW
    draw_text(title, big_font, color, (SCREEN_WIDTH // 2, 170))
    draw_text(f"PLAYER: {player_score}", font, WHITE, (SCREEN_WIDTH // 2, 260))
    draw_text(f"BOT: {bot_score}", font, WHITE, (SCREEN_WIDTH // 2, 295))
    draw_button(restart_button, "PLAY AGAIN")
    draw_button(menu_button, "MAIN MENU")

def spawn_player():
    global player_piece, player_next
    player_piece = player_next
    player_piece.x = COLS // 2 - len(player_piece.shape[0]) // 2
    player_piece.y = 0
    player_next = Piece()

def spawn_bot():
    global bot_piece, bot_next
    bot_piece = bot_next
    bot_piece.x = COLS // 2 - len(bot_piece.shape[0]) // 2
    bot_piece.y = 0
    bot_next = Piece()

def lock_player():
    global player_score, player_piece
    lock_piece(player_piece, player_board)
    lines = clear_lines(player_board)
    player_score += calculate_score(lines)
    spawn_player()
    if not valid_position(player_piece, player_board):
        finish_game("bot")

def finish_game(who_wins):
    global state, winner, best_score
    winner = who_wins
    if player_score > best_score:
        best_score = player_score
        save_best_score(best_score)
    state = GAME_OVER

reset_game()

running = True
while running:
    dt = clock.tick(FPS)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    reset_game()
                    state = GAME
                elif help_button.collidepoint(event.pos):
                    state = HELP

        elif state == HELP:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    state = MENU

        elif state == GAME_OVER:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    reset_game()
                    state = GAME
                elif menu_button.collidepoint(event.pos):
                    state = MENU

        elif state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = MENU
                elif event.key == pygame.K_LEFT:
                    if valid_position(player_piece, player_board, dx=-1):
                        player_piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if valid_position(player_piece, player_board, dx=1):
                        player_piece.x += 1
                elif event.key == pygame.K_UP:
                    old_shape = [row[:] for row in player_piece.shape]
                    old_x = player_piece.x
                    player_piece.rotate()
                    if not valid_position(player_piece, player_board):
                        player_piece.x -= 1
                        if not valid_position(player_piece, player_board):
                            player_piece.x += 2
                            if not valid_position(player_piece, player_board):
                                player_piece.shape = old_shape
                                player_piece.x = old_x
                elif event.key == pygame.K_SPACE:
                    while valid_position(player_piece, player_board, dy=1):
                        player_piece.y += 1
                    lock_player()

    if state == GAME:
        drop_speed = player_drop_delay
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            drop_speed = 60

        if now - player_drop_timer >= drop_speed:
            if valid_position(player_piece, player_board, dy=1):
                player_piece.y += 1
            else:
                lock_player()
            player_drop_timer = now

        if not bot_thinking:
            bot_thinking = True
            bot_drop_timer = now + 180

        if bot_thinking and now >= bot_drop_timer:
            execute_bot_move()
            spawn_bot()
            bot_thinking = False
            if not valid_position(bot_piece, bot_board):
                finish_game("player")

    if state == MENU:
        draw_menu()
    elif state == HELP:
        draw_help()
    elif state == GAME:
        screen.fill(BLACK)
        draw_top_panel()
        draw_board(player_board, 0, player_piece, "PLAYER")
        draw_board(bot_board, FIELD_WIDTH + 40, bot_piece, "BOT")
        pygame.draw.line(screen, GRID, (FIELD_WIDTH + 20, TOP_PANEL), (FIELD_WIDTH + 20, SCREEN_HEIGHT), 2)
    elif state == GAME_OVER:
        draw_game_over()

    pygame.display.flip()

pygame.quit()
