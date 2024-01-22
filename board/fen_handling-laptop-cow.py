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


def bitboards_to_fen(bitboards):
    # Mapping of piece types to FEN abbreviations
    piece_mapping = {0: "p", 1: "n", 2: "b", 3: "r", 4: "q", 5: "k"}

    # Extract bitboards for each piece type, all white pieces, all black pieces, castling rights, and en passant target
    (
        pawn_board,
        knight_board,
        bishop_board,
        rook_board,
        queen_board,
        king_board,
        white_pieces_board,
        black_pieces_board,
        castling_rights,
        en_passant_target,
    ) = bitboards

    # Convert bitboards to FEN piece placement
    piece_placement = ""
    for rank in range(7, -1, -1):  # Loop through ranks in reverse order
        empty_count = 0  # Count consecutive empty squares
        for file in range(8):
            square = rank * 8 + file
            piece = next(
                (
                    piece_mapping[piece_type]
                    for piece_type, piece_board in enumerate(
                        [
                            pawn_board,
                            knight_board,
                            bishop_board,
                            rook_board,
                            queen_board,
                            king_board,
                        ]
                    )
                    if (piece_board & np.uint64(1) << np.uint64(square)) != 0
                ),
                None,
            )
            if piece is not None:
                # Piece found, append empty count and piece to FEN
                if empty_count > 0:
                    piece_placement += str(empty_count)
                    empty_count = 0
                piece_placement += piece
            else:
                # Empty square, increase empty count
                empty_count += 1

        if empty_count > 0:
            # Append remaining empty count for the rank
            piece_placement += str(empty_count)

        if rank > 0:
            # Separate ranks with '/'
            piece_placement += "/"

    # Determine active color
    active_color = "w" if white_pieces_board != 0 else "b"

    # Determine castling rights in FEN
    castling_fen = ""
    if castling_rights & np.uint64(0b1000):
        castling_fen += "K"
    if castling_rights & np.uint64(0b0100):
        castling_fen += "Q"
    if castling_rights & np.uint64(0b0010):
        castling_fen += "k"
    if castling_rights & np.uint64(0b0001):
        castling_fen += "q"

    # Determine en passant target square in FEN
    en_passant_fen = (
        "-"
        if en_passant_target == 0
        else f"{chr((en_passant_target % 8) + ord('a'))}{8 - (en_passant_target // 8)}"
    )

    return f"{piece_placement} {active_color} {castling_fen} {en_passant_fen} 0 1"


fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
bitboard_array = fen_to_bitboards(fen_string)
converted_fen = bitboards_to_fen(bitboard_array)

print("Original FEN:", fen_string)
print("Converted FEN:", converted_fen)
