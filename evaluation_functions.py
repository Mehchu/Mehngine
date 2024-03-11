import numpy as np


class EvaluationFunction:
    def __init__(self) -> None:
        # Piece values
        self.piece_values = {
            "P": 100,
            "N": 325,
            "B": 350,
            "R": 550,
            "Q": 900,
            "K": 99999,
        }

    def evaluate(self, board) -> float:
        eval = 0

        # Material evaluation
        eval += 1.0 * self.evaluate_material(board)

        # Mobility evaluation
        eval += 1.21 * self.evaluate_mobility(board)

        # Pawn structure evaluation
        eval += 0.3 * self.evaluate_pawn_structure(board)

        # King safety evaluation
        eval += 0.420 * self.evaluate_king_safety(board)

        # Piece development evaluation
        eval += 0.3 * self.evaluate_piece_development(board)

        # Control of the center evaluation
        eval += 0.3 * self.evaluate_center_control(board)

        return eval

    def evaluate_material(
        self, board
    ) -> float:  # Evaluate how much material each side has
        eval = 0.0

        for square in range(64):  # Loop through each square on the chess board
            piece = board.determine_piece_on_square(square)

            if piece == None:  # Skip the square if there is no piece on it
                continue

            if np.uint64(1 << square) & board.all_bitboards[6]:
                eval += self.piece_values[
                    piece.upper()
                ]  # If the piece is the current player's, add the material

            else:
                eval -= self.piece_values[piece.upper()]  # Otherwise subtract the value

        return eval

    def evaluate_mobility(self, board) -> float:  # Evaluate how mobile each side is
        white_mobility = len(
            board.legal_moves
        )  # Determines how many legal moves white has

        board.flip_board()  # Makes it blacks turn so that black's moves can be generated
        black_mobility = len(
            board.legal_moves
        )  # Determines how many legal moves black has

        return white_mobility - black_mobility  # Returns the difference between them

    def evaluate_pawn_structure(self, board) -> float:
        # Evaluate pawn structure (e.g., isolated pawns, doubled pawns, passed pawns)
        eval = 0

        return eval

    def evaluate_king_safety(
        self, board
    ) -> float:  # Evaluate king safety (e.g., pawn shelter, open lines near the king)
        white_open_lines = []
        black_open_lines = []

        white_king_square = (
            board.all_bitboards[5] & board.all_bitboards[6]
        ).item().bit_length() - 1  # Finds the square that the white king is on

        white_open_lines.extend(
            board.generate_orthogonal_moves(white_king_square)
        )  # Add the horizontal and vertical lines open near the king
        white_open_lines.extend(
            board.generate_diagonal_moves(white_king_square)
        )  # Add the diagonal lines near the king

        board.flip_board()  # Flip the board to the other colour

        black_king_square = (
            board.all_bitboards[5] & board.all_bitboards[6]
        ).item().bit_length() - 1  # Find the black king

        black_open_lines.extend(
            board.generate_orthogonal_moves(black_king_square)
        )  # Add the horizontal and vertical lines open near the king
        black_open_lines.extend(
            board.generate_diagonal_moves(black_king_square)
        )  # Add the diagonal lines near the king

        return len(white_open_lines) - len(
            black_open_lines
        )  # Return the difference in king safety, not negated due to earlier board flips

    def evaluate_piece_development(self, board) -> float:
        # Evaluate piece development (e.g., pieces developed vs. undeveloped)
        eval = 0

        return eval

    def evaluate_center_control(self, board) -> float:
        # Evaluate control of the center (e.g., central pawn structure, piece placement)
        eval = 0

        return eval
