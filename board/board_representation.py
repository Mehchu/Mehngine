import numpy as np
from enum import Enum

from fen_handling import fen_to_bitboards

class PieceType(Enum):
    PAWNS = 0
    KNIGHTS = 1
    BISHOPS = 2
    ROOKS = 3
    QUEENS = 4
    KINGS = 5
    
class ChessBoard:
    def __init__(self, fen) -> None:
        # Convert the inputted fen to an array of binary integers
        temporary_bitboards = fen_to_bitboards(fen)

        # Initialise bitboards for each piece type using NumPy's unsigned integers for better performance
        self.pawns = np.uint64(temporary_bitboards[0])
        self.knights = np.uint64(temporary_bitboards[1])
        self.bishops = np.uint64(temporary_bitboards[2])
        self.rooks = np.uint64(temporary_bitboards[3])
        self.queens = np.uint64(temporary_bitboards[4])
        self.kings = np.uint64(temporary_bitboards[5])

        # Initialise general bitboards for each side and the board overall
        self.white_pieces = np.uint64(temporary_bitboards[6])
        self.black_pieces = np.uint64(temporary_bitboards[7])
        self.occupancy_mask = np.uint64(temporary_bitboards[8])

        # Initialise miscellaneous bitboards for special moves and nuanced evaluation
        self.attacked_squares = np.uint64(temporary_bitboards[9])
        self.pawn_structure = np.uint64(
            temporary_bitboards[10]
        )  # TODO: Is this really necessary?
        self.castling_rights = np.uint8(temporary_bitboards[11])
        self.en_passant_target = np.uint64(temporary_bitboards[12])

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
                self.occupancy_mask,
                self.attacked_squares,
                self.pawn_structure,
                self.castling_rights,
                self.en_passant_target,
            ]
        )

    def display_board(self):
        fen = 
