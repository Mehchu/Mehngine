import numpy as np

from board.board_representation import ChessBoard
from board.square_handling import decode_square, encode_square

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
TEST_FEN = "rnbqkbnr/ppppp2p/5p2/6p1/4P3/8/PPPP1PPP/RNBQKBNR"
OTHER_TEST_FEN = "7K/8/8/8/4P3/8/4p3/7k w KQkq - 0 1"


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


def main():
    position = ChessBoard(STARTING_FEN)

    """position.make_move("h8h7")
    position.display_board()

    print(position.evaluate())

    print(position.negamax2(1, -999, 999))"""

    while True:
        position.make_move(input())
        position.display_board()
        print(position.evaluate())

        for bitboard in range(len(position.all_bitboards)):
            if position.all_bitboards[bitboard] != position.previous_position[bitboard]:
                print(bitboard)


if __name__ == "__main__":
    main()
