import numpy as np


# Creates an exception via inheritance which can be raised when invalid notation is attempted to be parsed
class InvalidNotation(Exception):
    def __init__(self, notation: str):
        self.message = f'"{notation}" is invalid move notation'
        super().__init__(self.message)


# Creates an exception via inheritance which can be raised when an invalid square is attempted to be parsed
class InvalidSquare(Exception):
    def __init__(self, square: str):
        self.message = f'"{square}" is ian invalid square'
        super().__init__(self.message)


def decompose_notation(notation: str) -> str:
    try:
        # Tries to split the notation into a start square and an end square
        start_square = decode_square(notation[:2])
        end_square = decode_square(notation[2:4])

    except (
        ValueError
    ):  # Raised if the sub strings passed to decode_decode square are invalid
        raise InvalidNotation(notation)

    except (
        IndexError
    ):  # Raised if the notation is too short so cannot be sliced properly
        raise InvalidNotation(notation)

    try:
        promotion_piece = notation[
            4
        ]  # IF there is a 5th character in the string, it will be the promotion piece
        if (
            promotion_piece.upper() not in "PNBRQK"
        ):  # Don't allow promotion to pieces that don't exist
            raise InvalidNotation(notation)

    except (
        IndexError
    ):  # If the 5th character does not exist, then it is not promotion so no promotion piece is necessary
        promotion_piece = None

    return (start_square, end_square, promotion_piece)


# Function to convert a numerical square into an algebraic square
def encode_square(numerical_square: int) -> str:
    if isOnBoard(numerical_square):  # First checks if the square is on the board
        return chr(np.uint64(numerical_square % 8 + 97)) + str(
            numerical_square // 8 + 1
        )  # Converts the number to algebra e.g. 0 becomes a1, through mod and div and relevant ASCII conversions
    else:  # Raises an exception if the square is not on the board
        raise InvalidSquare(numerical_square)


# Function to convert an algebraic square to a numerical square
def decode_square(algebraic_square: str) -> int:
    square = (ord(algebraic_square[0]) - 97) + 8 * (
        int(algebraic_square[1]) - 1
    )  # Converts algebra to a number, through mod and div and relevant ASCII conversions
    if (
        isOnBoard(square)
        and algebraic_square[0]
        in "abcdefgh"  # Checks that the first character is in the first 8 letters of the alphabet
        and algebraic_square[1]
        in "12345678"  # Checks that the second character is in the first 8 integers of the positive integers
    ):
        return square  # Returns the converted square once validated
    else:
        raise InvalidSquare(
            algebraic_square
        )  # If an invalid square is converted then raise this exception


def isOnBoard(
    square: int,
) -> (
    bool
):  # Boolean expression to check if an inputted numerical square is on a standard chess board
    return 0 <= square < 64
