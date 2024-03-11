from timer import Timer  # Importing Timer class for measuring time
from board_representation import (
    ChessBoard,
    GameOver,
)  # Importing ChessBoard class and GameOver exception
from notation_handling import (
    InvalidNotation,
    decompose_notation,
)  # Importing InvalidNotation exception and decompose_notation function
from fen_handling import InvalidFEN  # Importing InvalidFEN exception
from search_algorithms import *  # Importing search algorithms
from evaluation_functions import *  # Importing evaluation functions

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"  # Default starting chess position
TEST_FEN = "k5q1/8/8/8/8/8/8/K4Q2 w - - 0 1"


def main():
    """
    Main function to start the game.
    """
    while True:
        customFEN = input(
            "Enter in a valid FEN for the position you wish the computer to play, leave blank for default: "
        )
        if len(customFEN) == 0:
            customFEN = STARTING_FEN
        try:
            board = ChessBoard(
                customFEN
            )  # Creating a ChessBoard object with the specified FEN
            break
        except InvalidFEN as e:
            print(f"{e.fen} is an invalid FEN, try again")

    playGame(board)


def playGame(board: ChessBoard):
    t = Timer()
    """
    Function to play the chess game.
    """
    depth = 4  # Chooses the depth that the program will run at

    board.display_board()  # Displaying the initial chess board

    while True:
        try:
            player_move = input(
                "Enter your move: "
            )  # Gets a move as input from the user

            if player_move == "exit":
                break

            decompose_notation(
                player_move
            )  # Decomposing the notation to check its validity

            if (
                player_move in board.generate_legal_moves()
            ):  # Checks legality of the player's move
                board.make_move(player_move)  # Making the player's move on the board
            else:
                print("Illegal move, try again")  # Lets the player try again
                continue
        except InvalidNotation:  # Informs the player if the notation is incorrect
            print(
                'Invalid notation, notation should be of the form "{starting_square}{destination_square}", try again'
            )
            continue

        t.start()
        move, score = negamax_alpha_beta_top(
            board, depth, -float("inf"), float("inf"), 1
        )  # Applying the negamax algorithm to get the best move for the computer

        t.stop()
        print(f"The evaluation is {-score/100}")
        try:
            board.make_move(move)  # Making the computer's move on the board
        except GameOver:
            return  # Exiting the game if it's over
        board.display_board()  # Displaying the updated board


if __name__ == "__main__":
    main()
