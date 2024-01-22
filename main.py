from board.board_representation import ChessBoard
from board.square_handling import decode_square

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
TEST_FEN = "rnbqkbnr/ppppp2p/5p2/6p1/4P3/8/PPPP1PPP/RNBQKBNR"
OTHER_TEST_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


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

    print(position.determine_piece_on_square(decode_square("e8")))


if __name__ == "__main__":
    main()
