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
                for _ in range(int(square)):
                    row.append(' ')
        array.append(row)
    return array

def fenToBinaryArray(fen):
    bitBoards = [0] * NUMBER_OF_BITBOARDS
    fen = (row for row in fen.split('/')) # Flip King and Queen for some reason with row[::-1]

    sqaure_index = 0
    for rank in fen:
        for file_index in range(len(rank)):
            if rank[file_index].isdigit():
                sqaure_index += int(rank[file_index]) # Use walrus maybe?
                continue
            piece = rank[file_index]
            # Sort piece into white/black bitboards
            if piece.upper() == piece:
                bitBoards[WHITE] += 2 ** sqaure_index
            else:
                bitBoards[BLACK] += 2 ** sqaure_index
            piece = piece.upper()
            # Sort piece into pawn/orthogonal/diagonal
            if piece == "P":
                bitBoards[PAWNS] += 2 ** sqaure_index
            if piece == "R" or piece == "Q":
                bitBoards[ORTHOGONALS] += 2 ** sqaure_index
            if piece == "B" or piece == "Q" :
                bitBoards[DIAGONALS] += 2 ** sqaure_index
            if piece == 'N':
                bitBoards[KNIGHTS] += 2 ** sqaure_index
            if piece == 'K':
                bitBoards[KINGS] += 2 ** sqaure_index

            sqaure_index += 1
          
    return [bitboard for bitboard in bitBoards]