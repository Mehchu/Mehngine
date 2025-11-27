import numpy as np


# Creates an exception for when an invalid FEN is detected
class InvalidFEN(Exception):
    def __init__(self, fen):
        self.message = f'"{fen}" is an invalid FEN'
        super().__init__(self.message)


def fen_to_bitboards(fen):
    try:
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
        )  # Appends the remaining bitboards to the array of all bitboards
        return bitboards
    except:
        raise InvalidFEN(fen)


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
    ) = bitboards  # Assigns each bitboard to a variable with a more aptly suited name

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
                    if (
                        piece_board & np.uint64(1) << np.uint64(square)
                    )  # If there is a piece on the square in the bitboard that is being searched, assign that piece to piece
                ),
                None,
            )
            if piece is not None:
                # Piece found, append empty count and piece to FEN
                if empty_count > 0:
                    piece_placement += str(empty_count)
                    empty_count = 0

                if white_pieces_board & np.uint64(1) << np.uint64(
                    square
                ):  # If the piece is a white piece, then add the uppercase version of the character
                    piece_placement += piece.upper()
                else:  # If not white, then it must be black so add the lowercase character
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
    if castling_rights & np.uint64(0b1000):  # Determines if white can castle kingside
        castling_fen += "K"
    if castling_rights & np.uint64(0b0100):  # Determines if white can castle queenside
        castling_fen += "Q"
    if castling_rights & np.uint64(0b0010):  # Determines if black can castle kingside
        castling_fen += "k"
    if castling_rights & np.uint64(0b0001):  # Determines if black can castle queenside
        castling_fen += "q"

    # Determine en passant target square in FEN
    en_passant_fen = (
        "-"
        if en_passant_target == 0
        else f"{chr((int(en_passant_target) % 8) + ord('a'))}{8 - (en_passant_target // 8)}"
    )

    return f"{piece_placement} {active_color} {castling_fen} {en_passant_fen} 0 1"


def display_chess_position(fen):

    # Create a mapping for piece characters
    piece_mapping = {
        "R": "♜",
        "N": "♞",
        "B": "♝",
        "Q": "♛",
        "K": "♚",
        "P": "♟",
        "r": "♖",
        "n": "♘",
        "b": "♗",
        "q": "♕",
        "k": "♔",
        "p": "♙",
        ".": "·",
    }

    # Parse FEN string
    rows = fen.split()[0].split("/")

    if len(rows) != 8:  # Detects if a board with an invalid number of rows is entered
        raise InvalidFEN(fen)

    display_str = ""
    for row in rows:  # Converts each row into a printable string
        display_row = []  # Starts with an empty row
        for char in row:  # Loops through each different piece in the row
            if char.isdigit():  # Detects how many empty squares appear in a row
                display_row.extend(
                    ["·"] * int(char)
                )  # Adds on the required amount of empty squares
            else:  # If it is not an empty square
                try:
                    display_row.append(
                        piece_mapping[char]
                    )  # Add on the corresponding piece
                except (
                    KeyError
                ):  # If the current character is not in the dictionary for symbols, then the FEN is invalid so raise that exception
                    raise InvalidFEN(fen)
        display_str += (
            " ".join(display_row) + "\n"
        )  # Join the converted row to the output string

    return display_str
