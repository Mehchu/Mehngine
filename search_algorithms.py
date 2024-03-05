from evaluation_functions import EvaluationFunction
import numpy as np


class TranspositionTable:
    def __init__(self):
        self.table = {}

    def lookup(self, key):
        return self.table.get(key)

    def store(self, key, score, depth):
        self.table[key] = {"score": score, "depth": depth}


class ZobristHash:
    def __init__(self, shape=(13,)):
        self.keys = np.random.randint(2**64, size=shape, dtype=np.uint64)

    def generate_key(self, position):
        return np.bitwise_xor.reduce(position * self.keys)


transposition_table = TranspositionTable()
eval = EvaluationFunction()
hash = ZobristHash()


def minimax(board, depth, maximizing_player):
    if depth == 0 or board.is_game_over():
        return None, eval.evaluate(board)

    if maximizing_player:
        best_move = None
        max_eval = -float("inf")

        for move in board.generate_legal_moves():
            board.make_move(move)

            _, eval = minimax(board, depth - 1, False)
            eval = -eval

            board.undo_move()

            if eval > max_eval:
                max_eval = eval
                best_move = move

        return best_move, max_eval
    else:
        best_move = None
        min_eval = float("inf")

        for move in board.generate_legal_moves():
            board.make_move(move)

            _, eval = minimax(board, depth - 1, True)
            eval = -eval

            board.undo_move()

            if eval < min_eval:
                min_eval = eval
                best_move = move

        return best_move, min_eval


def minimax_alpha_beta(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return None, eval.evaluate(board)

    if maximizing_player:
        best_move = None
        max_eval = -float("inf")

        for move in board.generate_legal_moves():
            board.make_move(move)

            _, eval = minimax_alpha_beta(board, depth - 1, alpha, beta, False)
            eval = -eval

            board.undo_move()

            if eval > max_eval:
                max_eval = eval
                best_move = move

            alpha = max(alpha, eval)
            if beta <= alpha:
                break

        return best_move, max_eval
    else:
        best_move = None
        min_eval = float("inf")

        for move in board.generate_legal_moves():
            board.make_move(move)

            _, eval = minimax_alpha_beta(board, depth - 1, alpha, beta, True)
            eval = -eval

            board.undo_move()

            if eval < min_eval:
                min_eval = eval
                best_move = move

            beta = min(beta, eval)
            if beta <= alpha:
                break

        return best_move, min_eval


def negamax(board, depth, color):
    if depth == 0 or board.is_game_over():
        return None, color * eval.evaluate(board)

    best_move = None
    max_score = -float("inf")

    for move in board.generate_legal_moves():
        board.make_move(move)

        _, score = negamax(board, depth - 1, -color)
        score = -score
        board.undo_move()

        if score > max_score:
            max_score = score
            best_move = move

    return best_move, max_score


def negamax_alpha_beta_top(board, depth, alpha, beta, color):
    key = hash.generate_key(
        board.all_bitboards
    )  # Generate a unique key for the current position

    if depth == 0:
        if board.is_game_over()[0]:
            print("White won" if board.is_game_over()[1] > 0 else "Black won")
        return None, color * eval.evaluate(board)

    if board.is_game_over()[0]:
        print("White won" if board.is_game_over()[1] > 0 else "Black won")
        return None, color * eval.evaluate(board)

    best_move = None
    best_score = -float("inf")

    for move in board.generate_legal_moves():
        board.make_move(move)
        score = -negamax_alpha_beta(board, depth - 1, -beta, -alpha, color)
        board.undo_move()

        if score > best_score:
            best_score = score
            best_move = move

        alpha = max(alpha, score)

        if alpha >= beta:
            break

    transposition_table.store(key, best_score, depth)
    return best_move, best_score


def negamax_alpha_beta(board, depth, alpha, beta, color):
    key = hash.generate_key(
        board.all_bitboards
    )  # Generate a unique key for the current position
    if (
        key in transposition_table.table
        and transposition_table.table[key]["depth"] >= depth
    ):
        return transposition_table.table[key]["score"]

    if depth == 0 or board.is_game_over()[0]:
        return color * eval.evaluate(board)

    best_score = -float("inf")

    for move in board.generate_legal_moves():
        board.make_move(move)
        score = -negamax_alpha_beta(board, depth - 1, -beta, -alpha, color)
        board.undo_move()

        best_score = max(best_score, score)
        alpha = max(alpha, score)

        if alpha >= beta:
            break

    transposition_table.store(key, best_score, depth)
    return best_score
