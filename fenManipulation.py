# TODO: Implement Knight/ King bitboards
# Castling rights / en passant (maybe implement in board.py)
#
#
NUMBER_OF_BITBOARDS = 7
WHITE = 0
BLACK = 1
PAWNS = 2
KNIGHTS = 3
DIAGONALS = 4
ORTHOGONALS = 5
KINGS = 6



def fenToArray(fen): # Not needed?
    array = []
    fen = fen.split('/')
    for rows in fen:
        row = []
        for square in rows:
            if square.upper() in "PNBRQK":
                row.append(square)
            elif square.isdigit():
                row.extend(' ' for _ in range(int(square)))
        array.append(row)
    return array

def fenToBinaryArray(fen):
    bitBoards = [0] * NUMBER_OF_BITBOARDS
    fen = iter(fen.split('/'))

    square_index = 0
    for rank in fen:
        for file_index in range(len(rank)):
            if rank[file_index].isdigit():
                square_index += int(rank[file_index]) # Use walrus maybe?
                continue
            piece = rank[file_index]
            # Sort piece into white/black bitboards
            if piece.upper() == piece:
                bitBoards[WHITE] += 1 << square_index
            else:
                bitBoards[BLACK] += 1 << square_index
            piece = piece.upper()
            # Sort piece into pawn/orthogonal/diagonal
            if piece == "P":
                bitBoards[PAWNS] += 1 << square_index
            if piece in ["R", "Q"]:
                bitBoards[ORTHOGONALS] += 1 << square_index
            if piece in ["B", "Q"]:
                bitBoards[DIAGONALS] += 1 << square_index
            if piece == 'N':
                bitBoards[KNIGHTS] += 1 << square_index
            if piece == 'K':
                bitBoards[KINGS] += 1 << square_index

            square_index += 1

    return list(bitBoards)