from timer import Timer

from board_representation import ChessBoard

from search_algorithms import *
from evaluation_functions import *


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
TEST_FEN = "rnbqkbnr/ppppp2p/5p2/6p1/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
OTHER_TEST_FEN = "7K/8/1P7/4p3/8/8/8/k7 w KQkq - 0 1"


def main():
    position = ChessBoard(STARTING_FEN)
    position.display_board()

    t = Timer()

    depth = 4

    while True:
        position.make_move(input())

        t.start()
        na_move, na_eval = negamax_alpha_beta_top(
            position, depth, -float("inf"), float("inf"), 1
        )
        t.stop()
        print(f"Negamax Alpha: {na_move, na_eval}")

        position.make_move(na_move)
        position.display_board()


if __name__ == "__main__":
    main()
