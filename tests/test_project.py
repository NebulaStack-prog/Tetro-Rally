import ast
import unittest
from pathlib import Path

tree = ast.parse((Path(__file__).resolve().parents[1] / "TetroRally.py").read_text(encoding="utf-8"))
names = {"create_board", "valid_position", "lock_piece", "clear_lines", "calculate_score", "get_column_heights", "count_holes", "board_score", "simulate_move", "bot_find_best_move"}
constants = {"COLS", "ROWS", "SHAPES", "COLORS", "CYAN", "YELLOW", "PURPLE", "ORANGE", "BLUE", "GREEN", "RED"}
nodes = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name in names) or (isinstance(n, ast.ClassDef) and n.name == "Piece") or (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in constants for t in n.targets))]
import random
ns = {"random": random}
exec(compile(ast.Module(body=nodes, type_ignores=[]), "TetroRally.py", "exec"), ns)

class GameTests(unittest.TestCase):
    def test_board(self):
        board = ns["create_board"]()
        self.assertEqual(len(board), 20)
        self.assertTrue(all(len(row) == 10 for row in board))

    def test_rotation(self):
        p = ns["Piece"](0)
        p.rotate()
        self.assertEqual(p.shape, [[1], [1], [1], [1]])

    def test_collision(self):
        p = ns["Piece"](0)
        board = ns["create_board"]()
        self.assertTrue(ns["valid_position"](p, board))
        self.assertFalse(ns["valid_position"](p, board, dx=-20))

    def test_lines(self):
        board = ns["create_board"]()
        board[-1] = [1] * 10
        self.assertEqual(ns["clear_lines"](board), 1)
        self.assertEqual(board[0], [None] * 10)

    def test_scoring(self):
        self.assertEqual([ns["calculate_score"](i) for i in range(5)], [0, 10, 30, 60, 100])

    def test_bot_move(self):
        board = ns["create_board"]()
        p = ns["Piece"](1)
        move = ns["bot_find_best_move"](p, board)
        self.assertIsNotNone(move)
        self.assertIsNotNone(ns["simulate_move"](p, board, move[1], move[2]))
        self.assertTrue(all(cell is None for row in board for cell in row))
