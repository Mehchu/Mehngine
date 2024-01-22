import unittest
import sys

print(sys.path)

from board.fen_handling import fen_to_bitboards


class TestFenConversion(unittest.TestCase):
    def test_starting_position(self):
        fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        self.assertEqual(
            fen_to_bitboards(fen_string),
        )


fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
bitboard_array = fen_to_bitboards(fen_string)
for i, bitboard in enumerate(bitboard_array):
    print(f"{i:2}: {bin(bitboard)[2:]:>64}")
