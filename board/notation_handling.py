import numpy as np


class InvalidNotation(Exception):
    def __init__(self, notation):
        self.message = f"{notation} is invalid move notation"
        super().__init(self.message)


def decompose_notation(notation):
    start_square = decode_square(notation[:2])
    end_square = decode_square(notation[2:4])
    try:
        promotion_piece = notation[4]
    except IndexError:
        promotion_piece = None

    return (start_square, end_square, promotion_piece)


def encode_square(numerical_square):
    try:
        return chr(np.uint64(numerical_square % 8 + 97)) + str(
            numerical_square // 8 + 1
        )
    except ValueError:
        raise InvalidNotation


def decode_square(algebraic_square):
    try:
        return (ord(algebraic_square[0]) - 97) + 8 * (int(algebraic_square[1]) - 1)
    except ValueError:
        raise InvalidNotation


def isOnBoard(square):
    return 0 <= square < 64
