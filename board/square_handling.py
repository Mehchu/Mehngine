import numpy as np


def decompose_notation(notation):
    start_square = decode_square(notation[:2])
    end_square = decode_square(notation[2:4])
    try:
        promotion_piece = notation[4]
    except:
        promotion_piece = None

    return (start_square, end_square, promotion_piece)


def encode_square(numerical_square):
    return chr(np.uint64(numerical_square % 8 + 97)) + str(numerical_square // 8 + 1)


def decode_square(algebraic_square):
    return (ord(algebraic_square[0]) - 97) + 8 * (int(algebraic_square[1]) - 1)


def isOnBoard(square):
    return 0 <= square < 64
