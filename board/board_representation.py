import numpy as np
from enum import Enum
from copy import deepcopy

from board.fen_handling import (
    fen_to_bitboards,
    bitboards_to_fen,
    display_chess_position,
)
from board.square_handling import (
    decompose_notation,
    decode_square,
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


class ChessBoard:
    def __init__(self, fen) -> None:
        # Convert the inputted fen to an array of binary integers
        temporary_bitboards = fen_to_bitboards(fen)
        # Initialise bitboards for each piece type using NumPy's unsigned integers for better performance
        self.pawns = temporary_bitboards[0]
        self.knights = temporary_bitboards[1]
        self.bishops = temporary_bitboards[2]

        self.rooks = temporary_bitboards[3]
        self.queens = temporary_bitboards[4]
        self.kings = temporary_bitboards[5]

        # Initialise general bitboards for each side and the board overall
        self.white_pieces = temporary_bitboards[6]
        self.black_pieces = temporary_bitboards[7]
        self.occupancy_mask = self.white_pieces | self.black_pieces

        # Initialise miscellaneous bitboards for special moves and nuanced evaluation
        self.attacked_squares = 0  # TODO
        self.pawn_structure = 0  # TODO: Is this really necessary?
        self.castling_rights = temporary_bitboards[8]
        self.en_passant_target = temporary_bitboards[9]

        # Collect all bitboards into a NumPy array
        self.all_bitboards = np.array(
            [
                self.pawns,  # 0
                self.knights,  # 1
                self.bishops,  # 2
                self.rooks,  # 3
                self.queens,  # 4
                self.kings,  # 5
                self.white_pieces,  # 6
                self.black_pieces,  # 7
                self.castling_rights,  # 8
                self.en_passant_target,  # 9
                self.occupancy_mask,  # 10
                self.attacked_squares,  # 11
                self.pawn_structure,  # 12
            ],
            dtype=np.uint64,
        )

        self.previous_position = self.all_bitboards.copy()  # TODO: make better

        self.pieceValue = {
            "P": 1,
            "N": 3,
            "B": 3,
            "R": 5,
            "Q": 9,
            "K": 99,
            "p": -1,
            "n": -3,
            "b": -3,
            "r": -5,
            "q": -9,
            "k": -99,
        }

    def make_move(self, long_algebraic_notation):  # TODO: Update misc bitboards
        self.previous_position = self.all_bitboards.copy()  # TODO: make better

        start_square, end_square, promotion_piece = decompose_notation(
            long_algebraic_notation
        )

        piece = self.determine_piece_on_square(start_square)

        if piece is None:
            return

        # Delete the piece, if any, on the end square
        for index in range(8):
            self.all_bitboards[index] = ~(
                ~self.all_bitboards[index] | np.uint64(1 << end_square)
            )

        # Identify the correct bitboard to update
        bitboard_index = PieceType[piece.upper()].value

        # Move the moving piece
        self.all_bitboards[bitboard_index] = ~(
            ~self.all_bitboards[bitboard_index] | np.uint64(1 << start_square)
        )

        if promotion_piece != None:
            piece = promotion_piece
            bitboard_index = PieceType[piece.upper()].value

        self.all_bitboards[bitboard_index] |= np.uint64(1 << end_square)

        # Update coloured bitboards
        if piece.isupper():
            self.all_bitboards[6] = ~(
                ~self.all_bitboards[6] | np.uint64(1 << start_square)
            )
            self.all_bitboards[6] |= np.uint64(1 << end_square)
        else:
            self.all_bitboards[7] = ~(
                ~self.all_bitboards[7] | np.uint64(1 << start_square)
            )
            self.all_bitboards[7] |= np.uint64(1 << end_square)

        # Update misc
        self.en_passant_target = 0

        if piece.upper() == "P" and abs(end_square // 8 - start_square // 8) == 2:
            self.en_passant_target = end_square

    def undoMove(self):  # Returns the board to its previous position TODO: Make better
        self.bitboards = self.previous_position.copy()

    def determine_piece_on_square(self, square):
        piece = None

        for index, bitboard in enumerate(self.all_bitboards[:6]):
            if bitboard & np.uint64(1 << square):
                piece = PieceType(index).name

                if np.uint64(self.black_pieces) & np.uint64(1 << square):
                    return piece.lower()

        return piece

    def generateOccupancyMask(self):
        self.occupancy_mask = self.white_pieces | self.black_pieces

    def generateOrthogonalMoves(self, square):  # #TODO: Change to offset method
        move_list = []

        offsets = [-8, -1, 1, 8]
        new_square = square

        # Moves up
        for _ in range(8):
            new_square += 8

            if not isOnBoard(new_square):
                break

            if np.uint64(1 << new_square) & self.occupancy_mask:
                if np.uint64(1 << new_square) & self.black_pieces:
                    move_list.append(
                        f"{encode_square(square)}{encode_square(new_square)}"
                    )
                break

            move_list.append(f"{encode_square(square)}{encode_square(new_square)}")

        new_square = square

        # Moves down
        for _ in range(8):
            new_square -= 8

            if not isOnBoard(new_square):
                break

            if np.uint64(1 << new_square) & self.occupancy_mask:
                if np.uint64(1 << new_square) & self.black_pieces:
                    move_list.append(
                        f"{encode_square(square)}{encode_square(new_square)}"
                    )
                break

            move_list.append(f"{encode_square(square)}{encode_square(new_square)}")

        new_square = square

        # Moves right
        for _ in range(8):
            new_square += 1

            if not isOnBoard(new_square) or square // 8 != new_square // 8:
                break

            if np.uint64(1 << new_square) & self.occupancy_mask:
                if np.uint64(1 << new_square) & self.black_pieces:
                    move_list.append(
                        f"{encode_square(square)}{encode_square(new_square)}"
                    )
                break

            move_list.append(f"{encode_square(square)}{encode_square(new_square)}")

        new_square = square

        # Moves left
        for _ in range(8):
            new_square -= 1

            if not isOnBoard(new_square) or square // 8 != new_square // 8:
                break

            if np.uint64(1 << new_square) & self.occupancy_mask:
                if np.uint64(1 << new_square) & self.black_pieces:
                    move_list.append(
                        f"{encode_square(square)}{encode_square(new_square)}"
                    )
                break

            move_list.append(f"{encode_square(square)}{encode_square(new_square)}")

        return move_list

    def generateDiagonalMoves(self, square):
        move_list = []

        new_square = square

        # Moves NE
        for _ in range(8):
            new_square += 9

            if not isOnBoard(new_square) or (new_square // 8 - square // 8) != (
                new_square % 8 - square % 8
            ):
                break

            if np.uint64(1 << new_square) & self.occupancy_mask:
                if np.uint64(1 << new_square) & self.black_pieces:
                    move_list.append(
                        f"{encode_square(square)}{encode_square(new_square)}"
                    )
                break

            move_list.append(f"{encode_square(square)}{encode_square(new_square)}")

        new_square = square

        # Moves NW
        for _ in range(8):
            new_square += 7

            if not isOnBoard(new_square) or (new_square // 8 - square // 8) != (
                new_square % 8 - square % 8
            ):
                break

            if np.uint64(1 << new_square) & self.occupancy_mask:
                if np.uint64(1 << new_square) & self.black_pieces:
                    move_list.append(
                        f"{encode_square(square)}{encode_square(new_square)}"
                    )
                break

            move_list.append(f"{encode_square(square)}{encode_square(new_square)}")

        new_square = square

        # Moves SE
        for _ in range(8):
            new_square -= 9

            if not isOnBoard(new_square) or (new_square // 8 - square // 8) != (
                new_square % 8 - square % 8
            ):
                break

            if np.uint64(1 << new_square) & self.occupancy_mask:
                if np.uint64(1 << new_square) & self.black_pieces:
                    move_list.append(
                        f"{encode_square(square)}{encode_square(new_square)}"
                    )
                break

            move_list.append(f"{encode_square(square)}{encode_square(new_square)}")

        new_square = square

        # Moves SW
        for _ in range(8):
            new_square -= 7

            if not isOnBoard(new_square) or (new_square // 8 - square // 8) != (
                new_square % 8 - square % 8
            ):
                break

            if np.uint64(1 << new_square) & self.occupancy_mask:
                if np.uint64(1 << new_square) & self.black_pieces:
                    move_list.append(
                        f"{encode_square(square)}{encode_square(new_square)}"
                    )
                break

            move_list.append(f"{encode_square(square)}{encode_square(new_square)}")

        return move_list

    def generateKnightMoves(self, square):
        offsets = [-17, -15, -10, -6, 6, 10, 15, 17]

        return [
            f"{encode_square(square)}{encode_square(square + offset)}"
            for offset in offsets
            if (
                isOnBoard(square + offset)
                and not np.uint64(1 << (square + offset)) & self.white_pieces
            )
        ]

    def generateKingMoves(self, square):
        offsets = [1, -1, -8, -8, 9, -9, 7, -7]

        return [
            f"{encode_square(square)}{encode_square(square + offset)}"
            for offset in offsets
            if (
                isOnBoard(square + offset)
                and not np.uint64(1 << (square + offset)) & self.white_pieces
            )
        ]

    def generatePawnMoves(self, square):
        move_list = []
        # Find forward pawn moves
        if not np.uint64(1 << (square + 8)) & self.occupancy_mask and isOnBoard(
            square + 8
        ):
            if (
                square // 8 == 1
                and not np.uint64(1 << (square + 16)) & self.occupancy_mask
            ):  # If the pawn is still on starting rank
                move_list.append(f"{encode_square(square)}{encode_square(square + 16)}")

            # Handle promotion
            if (square + 8) // 8 == 7:
                move_list.extend(
                    f"{encode_square(square)}{encode_square(square + 8)}{piece.name}"
                    for piece in PieceType
                    if piece.name != "P"
                )
            else:  # Move forward normally
                move_list.append(f"{encode_square(square)}{encode_square(square + 8)}")

        # Find captures
        if np.uint64(1 << (square + 7)) & self.black_pieces:
            # Handle promotion
            if (square + 7) // 8 == 7:
                move_list.extend(
                    f"{encode_square(square)}{encode_square(square + 7)}{piece.name}"
                    for piece in PieceType[1:]
                )
            else:
                move_list.append(f"{encode_square(square)}{encode_square(square + 7)}")

        if np.uint64(1 << (square + 9)) & self.black_pieces:
            # Handle promotion
            if (square + 9) // 8 == 7:
                move_list.extend(
                    f"{encode_square(square)}{encode_square(square + 9)}{piece.name}"
                    for piece in PieceType[1:]
                )
            else:
                move_list.append(f"{encode_square(square)}{encode_square(square + 9)}")

        # Handle en passant
        if square // 8 == self.en_passant_target // 8 and (
            (1 << square - 1) & (1 << self.en_passant_target)
            or (1 << square + 1) & (1 << self.en_passant_target)
        ):
            move_list.append(
                f"{encode_square(square)}{encode_square(self.en_passant_target + 8)}"
            )

        return move_list

    def generatePieceMoves(self, square: int) -> list:
        move_list = []
        piece = self.determine_piece_on_square(square)

        match piece:
            case "K":
                move_list.extend(self.generateKingMoves(square))
            case "Q":
                move_list.extend(self.generateOrthogonalMoves(square))
                move_list.extend(self.generateDiagonalMoves(square))
            case "R":
                move_list = self.generateOrthogonalMoves(square)
            case "B":
                move_list = self.generateDiagonalMoves(square)
            case "N":
                move_list = self.generateKnightMoves(square)
            case "P":
                move_list = self.generatePawnMoves(square)

        return move_list

    def generateAllLegalMoves(self):
        all_moves = []

        for square in range(64):
            if np.uint64(1 << square) & self.white_pieces:
                all_moves.extend(self.generatePieceMoves(square))

        return all_moves

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

    def flipAllBoards(self):
        for i in range(len(self.all_bitboards)):
            self.all_bitboards[i] = self.flip_bitboard(self.all_bitboards[i])

        white = self.white_pieces
        self.white_pieces = self.black_pieces
        self.white_pieces = white

    def evaluate(self) -> float:
        evaluation = 0.0

        for square in range(64):
            piece = self.determine_piece_on_square(square)

            if piece == None:
                continue

            if np.uint64(1 << square) & self.white_pieces:
                evaluation += self.pieceValue[piece]

            if np.uint64(1 << square) & self.black_pieces:
                evaluation += self.pieceValue[piece]

        return evaluation

    def negamax2(self, depth: int, alpha, beta) -> tuple[float, list]:
        if depth == 0:  # TODO: Implement end of game check
            return self.evaluate(), None

        searchBoard = deepcopy(self)

        max_value = -999
        best_move = ""

        for move in searchBoard.generateAllLegalMoves():
            searchBoard.make_move(move)  # Makes the move
            searchBoard.flipAllBoards()  # Makes it black to play
            value, _ = searchBoard.negamax2(
                depth - 1, -beta, -alpha
            )  # Recursively calls itself on the new position with black to play
            searchBoard.undoMove()

            if -value > max_value:
                max_value = -value
                best_move = move

            alpha = max(alpha, -value)
            if alpha >= beta:
                break

        return max_value, best_move

    def negamax(self, depth):
        if depth == 0:
            return self.evaluate()

        search_board = deepcopy(self)

        best_value = -999

        for move in search_board.generateAllLegalMoves():
            search_board.make_move(move)
            search_board.flipAllBoards()

            value = search_board.negamax(depth - 1)

            if -value > best_value:
                best_value = -value

            search_board.undoMove()

        return best_value

    def display_board(self):
        fen = bitboards_to_fen(self.all_bitboards[:10])
        display_chess_position(fen)
