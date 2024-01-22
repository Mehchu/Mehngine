import numpy as np
from enum import Enum

from board.fen_handling import fen_to_bitboards, bitboards_to_fen, display_fen


class PieceType(Enum):
    P = 0
    N = 1
    B = 2
    R = 3
    Q = 4
    K = 5


class ChessBoard:
    def __init__(self, fen) -> None:
        # Convert the inputted fen to an array of binary integers
        temporary_bitboards = fen_to_bitboards(fen)
        # Initialise bitboards for each piece type using NumPy's unsigned integers for better performance
        self.pawns = temporary_bitboards[0]
        self.knights = temporary_bitboards[1]
        self.bishops = temporary_bitboards[2]

        self.rooks = temporary_bitboards[3]
        self.queens = temporary_bitboards[4]
        self.kings = temporary_bitboards[5]

        # Initialise general bitboards for each side and the board overall
        self.white_pieces = temporary_bitboards[6]
        self.black_pieces = temporary_bitboards[7]
        self.occupancy_mask = self.white_pieces | self.black_pieces

        # Initialise miscellaneous bitboards for special moves and nuanced evaluation
        self.attacked_squares = 0  # TODO
        self.pawn_structure = 0  # TODO: Is this really necessary?
        self.castling_rights = temporary_bitboards[8]
        self.en_passant_target = temporary_bitboards[9]

        # Collect all bitboards into a NumPy array
        self.all_bitboards = np.array(
            [
                self.pawns,
                self.knights,
                self.bishops,
                self.rooks,
                self.queens,
                self.kings,
                self.white_pieces,
                self.black_pieces,
                self.castling_rights,
                self.en_passant_target,
                self.occupancy_mask,
                self.attacked_squares,
                self.pawn_structure,
            ],
            dtype=np.uint64,
        )

    def make_move(self, long_algebraic_notation):
        start_square, end_square, promotion_piece = decompose_notation(
            long_algebraic_notation
        )

        for bitboard in self.all_bitboards:
            pass

    def determine_piece_on_square(self, square):
        for index, bitboard in enumerate(self.all_bitboards[:6]):
            if bitboard & np.uint64(1 << square):
                break

        piece = PieceType(index).name

        print(printBitboard(self.black_pieces))

        if self.black_pieces & np.uint64(1 << square):
            print("Hola")
            return piece.lower()

        return piece

    def display_board(self):
        fen = bitboards_to_fen(self.all_bitboards[:10])
        print(fen)
        display_fen(fen)


def printBitboard(board: int) -> str:
    binBoard = bin(board)[2:]  # Remove the 0b which starts all binary strings

    while (
        len(binBoard) < 64
    ):  # Ensure binary is the required 64 bits long to be printed
        binBoard = f"0{binBoard}"

    count = 0
    stringToPrint = ""

    for square in binBoard:
        stringToPrint += f"{square} "
        count += 1

        if count == 8:  # Go onto a new line each time a file is filled
            stringToPrint += "\n"
            count = 0

    return stringToPrint
