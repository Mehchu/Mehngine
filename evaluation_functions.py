import numpy as np


class EvaluationFunction:
    def __init__(self) -> None:
        # Piece values
        self.piece_values = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 999}

    def evaluate(self, board) -> float:
        eval = 0

        # Material evaluation
        eval += 0.9 * self.evaluate_material(board)

        # Mobility evaluation
        eval += 0.5 * self.evaluate_mobility(board)

        # Pawn structure evaluation
        eval += 0.3 * self.evaluate_pawn_structure(board)

        # King safety evaluation
        eval += 0.3 * self.evaluate_king_safety(board)

        # Piece development evaluation
        eval += 0.3 * self.evaluate_piece_development(board)

        # Control of the center evaluation
        eval += 0.3 * self.evaluate_center_control(board)

        return eval

    def evaluate_material(self, board) -> float:
        eval = 0.0

        for square in range(64):
            piece = board.determine_piece_on_square(square)

            if piece == None:
                continue

            piece = piece.upper()

            if np.uint64(1 << square) & board.all_bitboards[6]:
                eval += self.piece_values[piece]

            else:
                eval -= self.piece_values[piece]

        return eval

    def evaluate_mobility(self, board) -> float:
        white_mobility = len(board.generate_legal_moves())

        board.flip_board()
        black_mobility = len(board.generate_legal_moves())

        return white_mobility - black_mobility

    def evaluate_pawn_structure(self, board) -> float:
        # Evaluate pawn structure (e.g., isolated pawns, doubled pawns, passed pawns)
        eval = 0

        return eval

    def evaluate_king_safety(self, board) -> float:
        # Evaluate king safety (e.g., pawn shelter, open lines near the king)
        white_open_lines = []
        black_open_lines = []

        white_king_square = (
            board.all_bitboards[5] & board.all_bitboards[6]
        ).item().bit_length() - 1

        white_open_lines.extend(board.generate_orthogonal_moves(white_king_square))
        white_open_lines.extend(board.generate_diagonal_moves(white_king_square))

        board.flip_board()

        black_king_square = (
            board.all_bitboards[5] & board.all_bitboards[6]
        ).item().bit_length() - 1

        black_open_lines.extend(board.generate_orthogonal_moves(black_king_square))
        black_open_lines.extend(board.generate_diagonal_moves(black_king_square))

        return len(black_open_lines) - len(white_open_lines)

    def evaluate_piece_development(self, board) -> float:
        # Evaluate piece development (e.g., pieces developed vs. undeveloped)
        eval = 0

        return eval

    def evaluate_center_control(self, board) -> float:
        # Evaluate control of the center (e.g., central pawn structure, piece placement)
        eval = 0

        return eval
