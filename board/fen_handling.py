import numpy as np


def fen_to_bitboards(fen):
    # Mapping of FEN piece abbreviations to piece types
    piece_mapping = {"p": 0, "n": 1, "b": 2, "r": 3, "q": 4, "k": 5}
    # Mapping of castle options to bitboard
    castling_mapping = {"K": 0b1000, "Q": 0b0100, "k": 0b0010, "q": 0b0001}

    # Initialize bitboards for each piece type, all white pieces, and all black pieces
    bitboards = [np.uint64(0)] * 6
    white_pieces = np.uint64(0)
    black_pieces = np.uint64(0)
    castling_rights = 0b0000  # 4-bit integer for castling rights
    en_passant_square = np.uint(0)

    # Extract the piece placement part of the FEN
    piece_placement = fen.split()[0]

    # Loop through each rank and file
    for rank, fen_rank in enumerate(reversed(piece_placement.split("/"))):
        file_index = 0

        # Loop through each character in the FEN rank
        for char in fen_rank:
            if char.isdigit():
                # Skip empty squares
                file_index += int(char)
            else:
                # Map the FEN piece abbreviation to the corresponding piece type
                piece_type = piece_mapping[char.lower()]

                # Set the corresponding bit in the bitboard
                bitboards[piece_type] |= np.uint64(1) << np.uint64(
                    rank * 8 + file_index
                )

                # Set the bit in the all white or all black pieces bitboards
                if char.isupper():  # White piece
                    white_pieces |= np.uint64(1) << np.uint64(rank * 8 + file_index)
                else:  # Black piece
                    black_pieces |= np.uint64(1) << np.uint64(rank * 8 + file_index)

                file_index += 1

    # Process castling rights
    castling_fen = fen.split()[2]
    for char in castling_fen:
        castling_rights |= castling_mapping.get(char, 0)

    # Process en passant target square
    en_passant_fen = fen.split()[3]
    if en_passant_fen != "-":
        en_passant_file = ord(en_passant_fen[0]) - ord("a")
        en_passant_rank = 8 - int(en_passant_fen[1])
        en_passant_square = en_passant_rank * 8 + en_passant_file

    # Add all white pieces, all black pieces, castling rights, and en passant target bitboards to the array
    bitboards.extend(
        [
            white_pieces,
            black_pieces,
            np.uint64(castling_rights),
            np.uint64(en_passant_square),
        ]
    )

    return bitboards
