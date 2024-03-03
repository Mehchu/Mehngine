from timer import Timer

from board_representation import ChessBoard

from search_algorithms import *
from evaluation_functions import *


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
TEST_FEN = "rnbqkbnr/ppppp2p/5p2/6p1/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
OTHER_TEST_FEN = "7K/8/1P7/4p3/8/8/8/k7 w KQkq - 0 1"


def all_search_algos(position, depth, t):
    ma_move, ma_eval = minimax_alpha_beta(
        position, depth, -float("inf"), float("inf"), True
    )
    print(f"Minimax Alpha: {ma_move, ma_eval}")

    m_move, m_eval = minimax(position, depth, True)

    print(f"Minimax: {m_move, m_eval}")

    n_move, n_eval = negamax(position, depth, True)

    print(f"Negamax: {n_move, n_eval}")


def main():
    position = ChessBoard(STARTING_FEN)

    t = Timer()

    depth = 4

    position.display_board()

    # print(position.negamax2(4, -float("inf"), float("inf"), True))

    # print(minimax_alpha_beta(position, 5, -float("inf"), float("inf"), True))

    while True:
        position.make_move(input())

        t.start()
        na_move, na_eval = negamax_alpha_beta(
            position, depth, -float("inf"), float("inf"), True
        )
        t.stop()
        print(f"Negamax Alpha: {na_move, na_eval}")

        position.make_move(na_move)
        position.display_board()


if __name__ == "__main__":
    main()
