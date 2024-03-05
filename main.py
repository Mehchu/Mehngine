from timer import Timer

from board_representation import ChessBoard, GameOver

from notation_handling import InvalidNotation, decompose_notation
from fen_handling import InvalidFEN

from search_algorithms import *
from evaluation_functions import *


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"  # Default starting chess position


def main():
    while True:
        customFEN = input(
            "Enter in a valid FEN for the position you wish the computer to play, leave blank for default: "
        )
        if len(customFEN) == 0:
            customFEN = STARTING_FEN
        try:
            board = ChessBoard(customFEN)
            break
        except InvalidFEN as e:
            print(f"{e.fen} is an invalid FEN, try again")

    playGame(board)


def playGame(board: ChessBoard):
    depth = 2  # Chooses the depth that the program will run at

    board.display_board()

    while True:
        try:
            player_move = input(
                "Enter your move: "
            )  # Gets a move as input from the user
            decompose_notation(player_move)
            if (
                player_move in board.generate_legal_moves()
            ):  # Checks legality of the player's move
                board.make_move(player_move)
            else:
                print("Illegal move, try again")  # Lets the player try again
                continue
        except InvalidNotation:  # Informs the player if the notation is incorrect
            print(
                'Invalid notation, notation should be of the form "{starting_square}{destination_square}", try again'
            )
            continue

        na_move, _ = negamax_alpha_beta_top(
            board, depth, -float("inf"), float("inf"), 1
        )
        try:
            board.make_move(na_move)
        except GameOver:
            return
        board.display_board()


if __name__ == "__main__":
    main()
