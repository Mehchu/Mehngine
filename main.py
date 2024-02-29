import numpy as np
import time

from board.board_representation import ChessBoard
from board.notation_handling import decode_square, encode_square

from board.search_algorithms import *


def time_function(func):
    start_time = time.time()
    func()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed Time: {elapsed_time} seconds")


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
TEST_FEN = "rnbqkbnr/ppppp2p/5p2/6p1/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
OTHER_TEST_FEN = "7K/8/1P7/4p3/8/8/8/k7 w KQkq - 0 1"


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

    position.display_board()

    # print(position.negamax2(4, -float("inf"), float("inf"), True))

    # print(minimax_alpha_beta(position, 5, -float("inf"), float("inf"), True))

    while True:
        position.make_move(input())
        position.display_board()
        position.flip_board()

        m_move, m_eval = minimax_alpha_beta(
            position, 5, -float("inf"), float("inf"), True
        )
        n_move, n_eval = negamax_alpha_beta(
            position, 5, -float("inf"), float("inf"), True
        )

        print(f"Minimax: {m_move, m_eval}")
        print(f"Negamax: {n_move, n_eval}")

        position.make_move(n_move)
        position.flip_board()
        position.display_board()


if __name__ == "__main__":
    time_function(main)
