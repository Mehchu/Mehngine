import numpy as np
from enum import Enum
from copy import deepcopy

from board.fen_handling import (
    fen_to_bitboards,
    bitboards_to_fen,
    display_chess_position,
)
from board.notation_handling import (
    decompose_notation,
    decode_square,
    encode_square,
    isOnBoard,
)


class PieceType(Enum):
    P = 0
    N = 1
    B = 2
    R = 3
    Q = 4
    K = 5


class GameOver(Exception):
    def __init__(self, player):
        print("Engine won" if player else "Player won")


class ChessBoard:
    def __init__(self, fen) -> None:
        # Convert the inputted fen to an array of binary integers
        temporary_bitboards = fen_to_bitboards(fen)

        # Collect all bitboards into a NumPy array TODO: Can be done better
        self.all_bitboards = np.array(
            [
                # Initialise bitboards for each piece type using NumPy's unsigned integers for better performance
                temporary_bitboards[0],  # Pawns, 0
                temporary_bitboards[1],  # Knights, 1
                temporary_bitboards[2],  # Bishops, 2
                temporary_bitboards[3],  # Rooks, 3
                temporary_bitboards[4],  # Queens, 4
                temporary_bitboards[5],  # Kings, 5
                # Initialise general bitboards for each side and the board overall
                temporary_bitboards[6],  # White, 6
                temporary_bitboards[7],  # Black, 7
                # Initialise miscellaneous bitboards for special moves and nuanced evaluation
                temporary_bitboards[8],  # Castling, 8
                temporary_bitboards[9],  # En passant, 9
                temporary_bitboards[6] | temporary_bitboards[7],  # Occupancy mask, 10
                0,  # Attacked squares, 11 # TODO
                0,  # Pawn structure, 12 # TODO
            ],
            dtype=np.uint64,
        )

        self.previous_positions = [self.all_bitboards.copy()]  # TODO: make better

        self.pieceValue = {
            "P": 1,
            "N": 3,
            "B": 3,
            "R": 5,
            "Q": 9,
            "K": 999,
            "p": -1,
            "n": -3,
            "b": -3,
            "r": -5,
            "q": -9,
            "k": -999,
        }

        self.best_score = -float("inf")
        self.best_move = None

    def is_game_over(self):
        if (
            self.generateAllLegalMoves() == []
            or self.all_bitboards[5] & self.all_bitboards[6] == 0
            or self.all_bitboards[5] & self.all_bitboards[7] == 0
        ):
            return True
        return False

    def isEdge(self, start_square, dest_square):
        """
        Check if a move from start_square to dest_square crosses an edge of the chessboard.

        Args:
            start_square (int): The starting square index.
            dest_square (int): The destination square index.

        Returns:
            bool: True if the move crosses an edge, False otherwise.
        """
        # Define the board dimensions (8x8 chessboard)
        num_ranks = 8
        num_files = 8

        # Get file and rank indices of start and dest squares
        start_file = start_square % num_files
        start_rank = start_square // num_ranks
        dest_file = dest_square % num_files
        dest_rank = dest_square // num_ranks

        # Check if the move crosses an edge in any direction
        return (
            abs(dest_file - start_file) > 1
            or abs(dest_rank - start_rank)  # Check file difference
            > 1  # Check rank difference
        )

    def make_move(self, long_algebraic_notation):  # TODO: Update misc bitboards
        if long_algebraic_notation == None:
            raise GameOver(False)

        self.previous_positions.append(self.all_bitboards.copy())  # TODO: make better

        start_square, end_square, promotion_piece = decompose_notation(
            long_algebraic_notation
        )

        piece = self.determine_piece_on_square(start_square)

        if piece is None:
            return

        # Creates masks to turn off a specified bit
        try:
            start_mask = np.uint64(~(1 << start_square))
            end_mask = np.uint64(~(1 << end_square))
        except OverflowError:
            return

        # Delete the piece, if any, on the end square
        for index in range(8):
            self.all_bitboards[index] &= end_mask

        # Identify the correct bitboard to update
        bitboard_index = PieceType[piece.upper()].value

        # Delete the moving piece
        self.all_bitboards[bitboard_index] &= start_mask

        # Update the targeted bitboard for the new piece if applicable
        if promotion_piece != None:
            piece = promotion_piece
            bitboard_index = PieceType[piece.upper()].value

        # Updates the target bitboard with the new piece on the end square
        self.all_bitboards[bitboard_index] |= np.uint64(1 << end_square)

        # Update coloured bitboards
        if piece.isupper():
            self.all_bitboards[6] &= start_mask
            self.all_bitboards[6] |= np.uint64(1 << end_square)
        else:
            self.all_bitboards[7] &= start_mask
            self.all_bitboards[7] |= np.uint64(1 << end_square)

        # Update misc
        self.all_bitboards[9] = 0
        self.updateOccupancyMask()

        if piece.upper() == "P" and abs(end_square // 8 - start_square // 8) == 2:
            self.all_bitboards[9] = end_square

    def undo_move(self):  # Returns the board to its previous position TODO: Make better
        self.all_bitboards = self.previous_positions[-1]
        self.previous_positions.pop()

    def determine_piece_on_square(self, square):
        piece = None

        for index, bitboard in enumerate(self.all_bitboards[:6]):
            if bitboard & np.uint64(1 << square):
                piece = PieceType(index).name

                if np.uint64(self.all_bitboards[7]) & np.uint64(1 << square):
                    return piece.lower()

        return piece

    def updateOccupancyMask(self):
        self.all_bitboards[10] = (
            self.all_bitboards[6].copy() | self.all_bitboards[7].copy()
        )

    def generateOrthogonalMoves(self, square):
        move_list = []

        offsets = [-8, 8, -1, 1]

        # Moves up
        for offset in offsets:
            new_square = square

            for _ in range(8):
                new_square += offset

                # TODO: might work as algorithm for legal moves??
                # TODO: Can generate duplicate moves if legal square can be reached by looping
                if not isOnBoard(new_square) or (
                    new_square // 8 != square // 8 and new_square % 8 != square % 8
                ):
                    break

                if np.uint64(1 << new_square) & self.all_bitboards[10]:
                    if np.uint64(1 << new_square) & self.all_bitboards[7]:
                        move_list.append(
                            f"{encode_square(square)}{encode_square(new_square)}"
                        )
                    break

                move_list.append(f"{encode_square(square)}{encode_square(new_square)}")

        return move_list

    def generateDiagonalMoves(self, square):
        move_list = []

        offsets = [-9, 9, -7, 7]

        for offset in offsets:
            new_square = square

            for _ in range(8):
                new_square += offset

                if not isOnBoard(new_square) or abs(
                    (new_square // 8 - square // 8)
                ) != abs(new_square % 8 - square % 8):
                    break

                if np.uint64(1 << new_square) & self.all_bitboards[10]:
                    if np.uint64(1 << new_square) & self.all_bitboards[7]:
                        move_list.append(
                            f"{encode_square(square)}{encode_square(new_square)}"
                        )
                    break

                move_list.append(f"{encode_square(square)}{encode_square(new_square)}")

        return move_list

    def generateKnightMoves(self, square):
        offsets = [-17, -15, -10, -6, 6, 10, 15, 17]

        return [
            f"{encode_square(square)}{encode_square(square + offset)}"
            for offset in offsets
            if (
                isOnBoard(square + offset)
                and not np.uint64(1 << (square + offset)) & self.all_bitboards[6]
                and not self.isEdge(square, square + offset)
            )
        ]

    def generateKingMoves(self, square):
        offsets = [1, -1, -8, -8, 9, -9, 7, -7]

        return [
            f"{encode_square(square)}{encode_square(square + offset)}"
            for offset in offsets
            if (
                isOnBoard(square + offset)
                and not np.uint64(1 << (square + offset)) & self.all_bitboards[6]
            )
        ]

    def generatePawnMoves(self, square):
        move_list = []
        # Find forward pawn moves
        if (
            isOnBoard(square + 8)
            and not np.uint64(1 << (square + 8)) & self.all_bitboards[10]
        ):
            if (
                square // 8 == 1
                and not np.uint64(1 << (square + 16)) & self.all_bitboards[10]
            ):  # If the pawn is still on starting rank
                move_list.append(f"{encode_square(square)}{encode_square(square + 16)}")

            # Handle promotion
            if (square + 8) // 8 == 7:
                move_list.extend(
                    f"{encode_square(square)}{encode_square(square + 8)}{piece.name}"
                    for piece in PieceType
                    if piece.name != "P" and piece.name != "K"
                )
            else:  # Move forward normally
                move_list.append(f"{encode_square(square)}{encode_square(square + 8)}")

        # Find captures
        if np.uint64(1 << (square + 7)) & self.all_bitboards[7]:
            # Handle promotion
            if (square + 7) // 8 == 7:
                move_list.extend(
                    f"{encode_square(square)}{encode_square(square + 7)}{piece.name}"
                    for piece in PieceType
                    if piece.name != "P" and piece.name != "K"
                )
            else:
                move_list.append(f"{encode_square(square)}{encode_square(square + 7)}")
        try:
            if np.uint64(1 << (square + 9)) & self.all_bitboards[7]:
                # Handle promotion
                if (square + 9) // 8 == 7:
                    move_list.extend(
                        f"{encode_square(square)}{encode_square(square + 9)}{piece.name}"
                        for piece in PieceType
                        if piece.name != "P" and piece.name != "K"
                    )
                else:
                    move_list.append(
                        f"{encode_square(square)}{encode_square(square + 9)}"
                    )
        except OverflowError:
            pass

        # Handle en passant
        if square // 8 == self.all_bitboards[9] // 8 and (
            np.uint64(1 << square - 1) & (np.uint64(1) << self.all_bitboards[9])
            or np.uint64(1 << square + 1) & (np.uint64(1) << self.all_bitboards[9])
        ):
            move_list.append(
                f"{encode_square(square)}{encode_square(self.all_bitboards[9] + 8)}"
            )

        return move_list

    def generatePieceMoves(self, square: int) -> list:
        move_list = []
        piece = self.determine_piece_on_square(square)

        match piece:
            case "K":
                move_list.extend(self.generateKingMoves(square))
            case "Q":
                move_list.extend(self.generateOrthogonalMoves(square))
                move_list.extend(self.generateDiagonalMoves(square))
            case "R":
                move_list = self.generateOrthogonalMoves(square)
            case "B":
                move_list = self.generateDiagonalMoves(square)
            case "N":
                move_list = self.generateKnightMoves(square)
            case "P":
                move_list = self.generatePawnMoves(square)

        return move_list

    def generateAllLegalMoves(self):
        all_moves = []

        for square in range(64):
            if np.uint64(1 << square) & self.all_bitboards[6]:
                all_moves.extend(self.generatePieceMoves(square))

        return all_moves

    def flip_bitboard(
        self, bitboard
    ):  # Flips a bitboard to be from black's perspective

        h1 = np.uint64(0x5555555555555555)
        h2 = np.uint64(0x3333333333333333)
        h4 = np.uint64(0x0F0F0F0F0F0F0F0F)
        v1 = np.uint64(0x00FF00FF00FF00FF)
        v2 = np.uint64(0x0000FFFF0000FFFF)

        bitboard = ((bitboard >> np.uint64(1)) & h1) | ((bitboard & h1) << np.uint64(1))
        bitboard = ((bitboard >> np.uint64(2)) & h2) | ((bitboard & h2) << np.uint64(2))
        bitboard = ((bitboard >> np.uint64(4)) & h4) | ((bitboard & h4) << np.uint64(4))
        bitboard = ((bitboard >> np.uint64(8)) & v1) | ((bitboard & v1) << np.uint64(8))
        bitboard = ((bitboard >> np.uint64(16)) & v2) | (
            (bitboard & v2) << np.uint64(16)
        )
        bitboard = (bitboard >> np.uint64(32)) | (bitboard << np.uint64(32))
        return bitboard & np.uint64(0xFFFFFFFFFFFFFFFF)

    def flip_board(self):  # Flips each board to be from blacks perspective
        for i in range(len(self.all_bitboards)):
            self.all_bitboards[i] = self.flip_bitboard(self.all_bitboards[i])

        white = self.all_bitboards[6].copy()
        self.all_bitboards[6] = self.all_bitboards[7].copy()
        self.all_bitboards[7] = white.copy()

    def evaluate(self) -> float:  # TODO implement more complex evaluation
        evaluation = 0.0

        for square in range(64):
            piece = self.determine_piece_on_square(square)

            if piece == None:
                continue

            if np.uint64(1 << square) & self.all_bitboards[6]:
                evaluation += self.pieceValue[piece]

            if np.uint64(1 << square) & self.all_bitboards[7]:
                evaluation += self.pieceValue[piece]

        return evaluation

    def display_board(self):
        fen = bitboards_to_fen(self.all_bitboards[:10])
        print(display_chess_position(fen))

    def __repr__(self) -> str:
        fen = bitboards_to_fen(self.all_bitboards[:10])
        return display_chess_position(fen)

    def __str__(self) -> str:
        fen = bitboards_to_fen(self.all_bitboards[:10])
        return display_chess_position(fen)
