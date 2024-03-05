import numpy as np
from enum import Enum

from fen_handling import (
    fen_to_bitboards,
    bitboards_to_fen,
    display_chess_position,
)
from notation_handling import (
    decompose_notation,
    encode_square,
    isOnBoard,
)


class PieceType(Enum):
    P = 0
    N = 1
    B = 2
    R = 3
    Q = 4
    K = 5


class GameOver(Exception):
    def __init__(self, player):
        print("Engine won" if player else "Player won")


class ChessBoard:
    def __init__(self, fen) -> None:
        self.white_to_move = True
        # Convert the inputted fen to an array of binary integers
        temporary_bitboards = fen_to_bitboards(fen)

        # Collect all bitboards into a NumPy array
        self.all_bitboards = np.array(
            [
                # Initialise bitboards for each piece type using NumPy's unsigned integers for better performance
                temporary_bitboards[0],  # Pawns, 0
                temporary_bitboards[1],  # Knights, 1
                temporary_bitboards[2],  # Bishops, 2
                temporary_bitboards[3],  # Rooks, 3
                temporary_bitboards[4],  # Queens, 4
                temporary_bitboards[5],  # Kings, 5
                # Initialise general bitboards for each side and the board overall
                temporary_bitboards[6],  # White, 6
                temporary_bitboards[7],  # Black, 7
                # Initialise miscellaneous bitboards for special moves and nuanced evaluation
                temporary_bitboards[8],  # Castling, 8
                temporary_bitboards[9],  # En passant, 9
                temporary_bitboards[6] | temporary_bitboards[7],  # Occupancy mask, 10
                0,  # Attacked squares, 11 # TODO
                0,  # Pawn structure, 12 # TODO
            ],
            dtype=np.uint64,
        )

        self.previous_positions = [self.all_bitboards.copy()]  # TODO: make better

    def is_game_over(self):
        if len(self.generate_legal_moves()) == 0:  # Stalemate
            return True, 0

        if (
            not self.all_bitboards[5] & self.all_bitboards[6]
        ):  # White king has been captured
            return True, 999

        if (
            not self.all_bitboards[5] & self.all_bitboards[7]
        ):  # Black king has been captured
            return True, -999
        return False, 0

    def knight_moved_over_edge(self, start_square, dest_square):

        # Get file and rank indices of start and dest squares
        start_file = start_square % 8
        start_rank = start_square // 8
        dest_file = dest_square % 8
        dest_rank = dest_square // 8

        # Check if the move crosses an edge in any direction
        return (
            abs(dest_file - start_file) > 2
            or abs(dest_rank - start_rank)  # Check file difference
            > 2  # Check rank difference
        )

    def make_move(self, long_algebraic_notation):  # TODO: Update misc bitboards
        if long_algebraic_notation == None:
            raise GameOver(False)

        self.previous_positions.append(self.all_bitboards.copy())  # TODO: make better

        start_square, end_square, promotion_piece = decompose_notation(
            long_algebraic_notation
        )

        piece = self.determine_piece_on_square(start_square)

        if piece is None:
            return

        # Creates masks to turn off a specified bit
        try:
            start_mask = np.uint64(~(1 << start_square))
            end_mask = np.uint64(~(1 << end_square))
        except OverflowError:  # TODO: What causes this?
            self.all_bitboards[9] = 0
            self.update_occupancy_mask()
            
            self.flip_board()
            self.white_to_move = not self.white_to_move

            return

        # Delete the piece, if any, on the end square
        for index in range(8):
            self.all_bitboards[index] &= end_mask

        # Identify the correct bitboard to update
        bitboard_index = PieceType[piece.upper()].value

        # Delete the moving piece
        self.all_bitboards[bitboard_index] &= start_mask

        # Update the targeted bitboard for the new piece if applicable
        if promotion_piece != None:
            piece = promotion_piece
            bitboard_index = PieceType[piece.upper()].value

        # Updates the target bitboard with the new piece on the end square
        self.all_bitboards[bitboard_index] |= np.uint64(1 << end_square)

        # Update coloured bitboards
        if piece.isupper():
            self.all_bitboards[6] &= start_mask
            self.all_bitboards[6] |= np.uint64(1 << end_square)
        else:
            self.all_bitboards[7] &= start_mask
            self.all_bitboards[7] |= np.uint64(1 << end_square)

        # Update misc
        self.all_bitboards[9] = 0
        self.update_occupancy_mask()

        if piece.upper() == "P" and abs(end_square // 8 - start_square // 8) == 2:
            self.all_bitboards[9] = end_square

        self.flip_board()
        self.white_to_move = not self.white_to_move

    def undo_move(self):  # Returns the board to its previous position TODO: Make better
        self.all_bitboards = self.previous_positions[-1]
        self.previous_positions.pop()

    def determine_piece_on_square(self, square):
        for index in range(6):
            if self.all_bitboards[index] & np.uint64(1 << square):
                piece = PieceType(index).name
                return (
                    piece.lower()
                    if self.all_bitboards[7] & np.uint64(1 << square)
                    else piece
                )
        return None

    def update_occupancy_mask(self):
        self.all_bitboards[10] = self.all_bitboards[6] | self.all_bitboards[7]

    def generate_orthogonal_moves(self, square):
        move_list = []

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, up, down

        for dx, dy in directions:
            new_square = square + dx + 8 * dy

            while isOnBoard(new_square):
                if (
                    abs(new_square % 8 - square % 8) > 0
                    and abs(new_square // 8 - square // 8) > 0
                ):
                    break  # Move crosses board edge

                if np.uint64(1 << new_square) & self.all_bitboards[10]:
                    if np.uint64(1 << new_square) & self.all_bitboards[7]:
                        move_list.insert(
                            0, f"{encode_square(square)}{encode_square(new_square)}"
                        )
                    break

                move_list.append(f"{encode_square(square)}{encode_square(new_square)}")

                new_square += dx + 8 * dy

        return move_list

    def generate_diagonal_moves(self, square):
        move_list = []

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # NW, NE, SW, SE

        for dx, dy in directions:
            new_square = square + dx + 8 * dy

            while isOnBoard(new_square):
                if abs(new_square % 8 - square % 8) != abs(
                    new_square // 8 - square // 8
                ):
                    break  # Move is not diagonal

                if np.uint64(1 << new_square) & self.all_bitboards[10]:
                    if np.uint64(1 << new_square) & self.all_bitboards[7]:
                        move_list.insert(
                            0, f"{encode_square(square)}{encode_square(new_square)}"
                        )
                    break

                move_list.append(f"{encode_square(square)}{encode_square(new_square)}")

                new_square += dx + 8 * dy

        return move_list

    def generate_knight_moves(self, square):
        move_list = []

        # Unroll the a for loop for all possible knight moves for no loop overhead
        new_squares = [
            square - 17,
            square - 15,
            square - 10,
            square - 6,
            square + 6,
            square + 10,
            square + 15,
            square + 17,
        ]

        for new_square in new_squares:
            if (
                isOnBoard(new_square)
                and not np.uint64(1 << new_square) & self.all_bitboards[6]
            ):
                if not self.knight_moved_over_edge(square, new_square):
                    move_list.append(
                        f"{encode_square(square)}{encode_square(new_square)}"
                    )

        return move_list

    def generate_king_moves(self, square):
        offsets = [1, -1, -8, 8, 9, -9, 7, -7]

        return [
            f"{encode_square(square)}{encode_square(square + offset)}"
            for offset in offsets
            if (
                isOnBoard(square + offset)
                and not np.uint64(1 << (square + offset)) & self.all_bitboards[6]
            )
        ]

    def generate_pawn_moves(self, square):
        move_list = []
        # Find forward pawn moves
        if (
            isOnBoard(square + 8)
            and not np.uint64(1 << (square + 8)) & self.all_bitboards[10]
        ):
            if (
                square // 8 == 1
                and not np.uint64(1 << (square + 16)) & self.all_bitboards[10]
            ):  # If the pawn is still on starting rank
                move_list.append(f"{encode_square(square)}{encode_square(square + 16)}")

            # Handle promotion
            if (square + 8) // 8 == 7:
                for piece in PieceType:
                    if piece.name != "P" and piece.name != "K":
                        move_list.insert(
                            0,
                            (
                                f"{encode_square(square)}{encode_square(square + 8)}{piece.name}"
                            ),
                        )
            else:  # Move forward normally
                move_list.append(f"{encode_square(square)}{encode_square(square + 8)}")

        # Find captures
        try:
            if np.uint64(1 << (square + 7)) & self.all_bitboards[
                7
            ] and not self.knight_moved_over_edge(square, square + 7):
                # Handle promotion
                if (square + 7) // 8 == 7:
                    for piece in PieceType:
                        if piece.name != "P" and piece.name != "K":
                            move_list.insert(
                                0,
                                (
                                    f"{encode_square(square)}{encode_square(square + 7)}{piece.name}"
                                ),
                            )
                else:
                    move_list.insert(
                        0, f"{encode_square(square)}{encode_square(square + 7)}"
                    )
        except:
            print("Probably fix this")
        try:
            if np.uint64(1 << (square + 9)) & self.all_bitboards[
                7
            ] and not self.knight_moved_over_edge(square, square + 9):
                # Handle promotion
                if (square + 9) // 8 == 7:
                    for piece in PieceType:
                        if piece.name != "P" and piece.name != "K":
                            move_list.insert(
                                0,
                                (
                                    f"{encode_square(square)}{encode_square(square + 9)}{piece.name}"
                                ),
                            )
                else:
                    move_list.insert(
                        0, f"{encode_square(square)}{encode_square(square + 9)}"
                    )
        except OverflowError:
            print("Probably fix this")

        # Handle en passant
        if square // 8 == self.all_bitboards[9] // 8 and (
            np.uint64(1 << square - 1) & (np.uint64(1) << self.all_bitboards[9])
            or np.uint64(1 << square + 1) & (np.uint64(1) << self.all_bitboards[9])
        ):
            move_list.insert(
                0, f"{encode_square(square)}{encode_square(self.all_bitboards[9] + 8)}"
            )

        return move_list

    def generate_piece_moves(self, square: int) -> list:
        move_list = np.array([])
        piece = self.determine_piece_on_square(square)

        match piece:
            case "K":
                move_list.extend(self.generate_king_moves(square))
            case "Q":
                move_list.extend(self.generate_orthogonal_moves(square))
                move_list.extend(self.generate_diagonal_moves(square))
            case "R":
                move_list = self.generate_orthogonal_moves(square)
            case "B":
                move_list = self.generate_diagonal_moves(square)
            case "N":
                move_list = self.generate_knight_moves(square)
            case "P":
                move_list = self.generate_pawn_moves(square)

        return move_list

    def generate_legal_moves(self):
        move_list = []

        for square in range(64):
            if np.uint64(1 << square) & self.all_bitboards[6]:
                piece = self.determine_piece_on_square(square)

                match piece:  # Insertion to order the moves
                    case "K":
                        move_list.extend(self.generate_king_moves(square))
                    case "Q":
                        move_list.extend(self.generate_orthogonal_moves(square))
                        move_list.extend(self.generate_diagonal_moves(square))
                    case "R":
                        move_list.extend(self.generate_orthogonal_moves(square))
                    case "B":
                        move_list.extend(self.generate_diagonal_moves(square))
                    case "N":
                        move_list.extend(self.generate_knight_moves(square))
                    case "P":
                        move_list.extend(self.generate_pawn_moves(square))

        return np.array(move_list).flatten()

    def flip_bitboard(
        self, bitboard
    ):  # Flips a bitboard to be from black's perspective

        h1 = np.uint64(0x5555555555555555)
        h2 = np.uint64(0x3333333333333333)
        h4 = np.uint64(0x0F0F0F0F0F0F0F0F)
        v1 = np.uint64(0x00FF00FF00FF00FF)
        v2 = np.uint64(0x0000FFFF0000FFFF)

        bitboard = ((bitboard >> np.uint64(1)) & h1) | ((bitboard & h1) << np.uint64(1))
        bitboard = ((bitboard >> np.uint64(2)) & h2) | ((bitboard & h2) << np.uint64(2))
        bitboard = ((bitboard >> np.uint64(4)) & h4) | ((bitboard & h4) << np.uint64(4))
        bitboard = ((bitboard >> np.uint64(8)) & v1) | ((bitboard & v1) << np.uint64(8))
        bitboard = ((bitboard >> np.uint64(16)) & v2) | (
            (bitboard & v2) << np.uint64(16)
        )
        bitboard = (bitboard >> np.uint64(32)) | (bitboard << np.uint64(32))
        return bitboard & np.uint64(0xFFFFFFFFFFFFFFFF)

    def flip_board(self):  # Flips each board to be from blacks perspective
        for i in range(len(self.all_bitboards)):
            self.all_bitboards[i] = self.flip_bitboard(self.all_bitboards[i])

        white = self.all_bitboards[6].copy()
        self.all_bitboards[6] = self.all_bitboards[7].copy()
        self.all_bitboards[7] = white.copy()

    def display_board(self):
        fen = bitboards_to_fen(self.all_bitboards[:10])
        print(display_chess_position(fen))

    def __repr__(self) -> str:
        fen = bitboards_to_fen(self.all_bitboards[:10])
        return display_chess_position(fen)

    def __str__(self) -> str:
        fen = bitboards_to_fen(self.all_bitboards[:10])
        return display_chess_position(fen)
