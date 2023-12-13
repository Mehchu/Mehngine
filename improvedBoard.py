from math import inf

from bitBoardManipulation import *
from fenManipulation import fenToBinaryArray, fenToArray

from enum import Enum
from copy import deepcopy


def printArrays(arrays):
    border = "-" * 26
    print(border)
    for array in arrays:
        print("| " + " ".join(str(element) for element in array) + " |")
    print(border[:-1])
    
class PieceType(Enum):
    WHITE = 0
    BLACK = 1
    PAWNS = 2
    KNIGHTS = 3
    DIAGONALS = 4  # Assuming this represents Bishops
    ORTHOGONALS = 5  # Assuming this represents Rooks
    KINGS = 6


class ChessPiece:
    def __init__(self, binary, piece):
        self.binary = binary
        self.piece = piece


class Board:
    def __init__(self, fen: str) -> None:
        # Updates when game ends (by draw or by checkmate)
        self.gameState = 0

        # Converts the initial FEN into an array of bitboards
        self.bitboards = fenToBinaryArray(fen)
        self.previous_position = self.bitboards.copy()

        # Stores number of bitboards for later use
        self.numberOfBitboards = len(PieceType)

        # Binary representation of a square across all bitboards to its corresponding piece
        self.binaryToPiece = {'1010000': 'P',
                              '1001000': 'N',
                              '1000100': 'B',
                              '1000010': 'R',
                              '1000110': 'Q',
                              '1000001': 'K',
                              '0110000': 'p',
                              '0101000': 'n',
                              '0100100': 'b',
                              '0100010': 'r',
                              '0100110': 'q',
                              '0100001': 'k'}

        self.bitboardConversion = {'P': PieceType.PAWNS,
                                   'N': PieceType.KNIGHTS,
                                   'B': PieceType.DIAGONALS,
                                   'R': PieceType.ORTHOGONALS,
                                   'K': PieceType.KINGS
                                   }

        self.pieceValue = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 99,
                           'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': -99}

        self.RANKS = range(8)
        self.FILES = range(8)

    def __repr__(self) -> str:
        return "/".join(self.rank_to_fen(rank) for rank in range(8)) # Returns the FEN of the position by combining the FEN of each rank 

    def rank_to_fen(self, rank: int) -> str: # COnverts a rank of a position into its corresponding FEN
        empty = 0
        fen = ""
        for file in range(8):
            piece = self.determinePieceOnSquare(rank * 8 + file)
            if piece == ' ':
                empty += 1
            else:
                if empty:
                    fen += str(empty)
                    empty = 0
                fen += piece
        if empty:
            fen += str(empty)
        return fen

    def makeMove(self, startSquare: int, targetSquare: int):  # Change order, make efficient?
        self.previous_position = self.bitboards.copy()
        piece = self.determinePieceOnSquare(
            startSquare)  # Determine piece that is moving

        if piece == -1:  # Blank space means invalid move
            raise ValueError(
                f"{startSquare} is a blank square and therefore should not be able to make a move")

        if piece == piece.lower():
            raise ValueError(
                f"{startSquare} is a black piece and therefore should not be able to make a move")

        # Removes white piece from starting square
        self.bitboards[PieceType.WHITE.value] &= ~(1 << startSquare)
        # Places white piece on target square
        self.bitboards[PieceType.WHITE.value] |= 1 << targetSquare

        # Remove all target square data
        for bitboard in range(self.numberOfBitboards - 1):
            self.bitboards[bitboard + 1] &= ~(1 << targetSquare)

        if piece == 'Q':
            self.bitboards[PieceType.ORTHOGONALS.value] &= ~(1 << startSquare)
            self.bitboards[PieceType.ORTHOGONALS.value] |= 1 << targetSquare

            self.bitboards[PieceType.DIAGONALS.value] &= ~(1 << startSquare)
            self.bitboards[PieceType.DIAGONALS.value] |= 1 << targetSquare

            return

        self.bitboards[self.bitboardConversion[piece].value] &= ~(1 << startSquare)
        self.bitboards[self.bitboardConversion[piece].value] |= 1 << targetSquare

    def undoMove(self): # Returns the board to its previous position
        self.bitboards = self.previous_position.copy()

    def determinePieceOnSquare(self, square: int) -> str:
        binString = ''.join(
            '1' if bitboard & 1 << square != 0 else '0'
            for bitboard in self.bitboards
        )
        if binString == '0' * self.numberOfBitboards:  # If an empty square
            return ' '

        # Convert the binary string to a piece character
        return self.binaryToPiece[binString]

    def generateOccupancyMask(self) -> int: # Bitwise OR each bitboard together to return mask of all pieces without any piece data
        occupancyMask = 0

        for bitboard in self.bitboards:
            occupancyMask |= bitboard

        return occupancyMask

    def generateWhite(self) -> int:
        return self.generateOccupancyMask() & self.bitboards[PieceType.WHITE.value]

    def generateBlack(self) -> int:
        return self.generateOccupancyMask() & self.bitboards[PieceType.BLACK.value]

    def generateMovesInDirection(self, square, direction_offsets, occupancy_mask, own_pieces):
        moves = 0
        for offset in direction_offsets:
            new_square = square + offset
            while isSquareOnBoard(new_square) and abs(getFile(new_square) - getFile(new_square - offset)) <= 1 and abs(getRank(new_square) - getRank(new_square - offset)) <= 1:
                if 1 << new_square & occupancy_mask:
                    if 1 << new_square & own_pieces:
                        moves |= 1 << new_square
                    break
                moves |= 1 << new_square
                new_square += offset
        
        return moves

    def generateKingMoves(self, whitePieces : int, square : int):
        moves = 0
        offsets = [-9, -8, -7, -1, 1, 7, 8, 9]
        
        for offset in offsets:
            newSquare = square + offset
            if isSquareOnBoard(newSquare) and 1 << (newSquare) & whitePieces == 0:
                moves += 1 << (square + offset)
        
        return moves

    def generatePawnMoves(self, ocuupancyMask: int, blackPieces: int, square: int) -> int:
        pawnMoves = 0
        # Find forward pawn moves
        if 1 << (square - 8) & ocuupancyMask == 0 and isSquareOnBoard(square - 8):
            pawnMoves |= 1 << (square - 8)

            if getRank(square) == 6:  # If the pawn is still on starting rank
                pawnMoves |= 1 << (square - 16)

        # Find captures
        if 1 << (square - 7) & blackPieces != 0:
            pawnMoves |= 1 << (square - 7)

        if 1 << (square - 9) & blackPieces != 0:
            pawnMoves |= 1 << (square - 9)

        return pawnMoves

    def generateKnightMoves(self, whitePieces: int, square: int):
        knightMoves = 0
        offsets = [-17, -15, -10, -6, 6, 10, 15, 17]

        for offset in offsets:
            newSquare = square + offset
            if isSquareOnBoard(newSquare) and 1 << (newSquare) & whitePieces == 0 and abs(getFile(newSquare) - getFile(square)) <= 2:
                knightMoves += 1 << (square + offset)

        return knightMoves

    def generateDiagonalMoves(self, occupancy_mask, white_pieces, square):
        return self.generateMovesInDirection(square, [9, -9, 7, -7], occupancy_mask, white_pieces)

    def generateOrthogonalMoves(self, occupancy_mask, white_pieces, square):
        return self.generateMovesInDirection(square, [1, -1, 8, -8], occupancy_mask, white_pieces)

    def generatePieceMoves(self, square: int) -> list:
        moves = 0

        occupancyMask = self.generateOccupancyMask()
        whitePieces = self.generateWhite()
        blackPieces = self.generateBlack()
        piece = self.determinePieceOnSquare(square)

        match piece:
            case 'K':
                moves = self.generateKingMoves(whitePieces, square)
            case 'Q':
                moves = self.generateOrthogonalMoves(
                    occupancyMask, whitePieces, square) | self.generateDiagonalMoves(occupancyMask, whitePieces, square)
            case 'R':
                moves = self.generateOrthogonalMoves(
                    occupancyMask, whitePieces, square)
            case 'B':
                moves = self.generateDiagonalMoves(
                    occupancyMask, whitePieces, square)
            case 'N':
                moves = self.generateKnightMoves(whitePieces, square)
            case 'P':
                # Make use white pieces maybe?
                moves = self.generatePawnMoves(
                    occupancyMask, blackPieces, square)

        return self.turnPieceMovesIntoPairsOfMoves(square, moves)

    def turnPieceMovesIntoPairsOfMoves(self, startSquare, moves) -> list:
        return [
            [startSquare, square]
            for square in range(64)
            if 1 << square & moves != 0
        ]

    def generateAllLegalMoves(self) -> list:
        pairedMoves = []

        whitePieces = self.generateWhite()
        for square in range(64):
            if 1 << square & whitePieces != 0:
                if pairedMove := self.generatePieceMoves(square):
                    pairedMoves.extend(pairedMove)
        return pairedMoves

    def evaluate(self) -> float:
        evaluation = 0.0
        whitePieces = self.generateWhite()
        blackPieces = self.generateBlack()

        for square in range(64):
            piece = self.determinePieceOnSquare(square)

            if piece == -1:
                continue

            if 1 << square & whitePieces != 0:
                evaluation += self.pieceValue[piece]

            if 1 << square & blackPieces != 0:
                evaluation += self.pieceValue[piece]

        return evaluation

    def flip_bitboard(self, bitboard: int) -> int:
        h1 = 0x5555555555555555
        h2 = 0x3333333333333333
        h4 = 0x0F0F0F0F0F0F0F0F
        v1 = 0x00FF00FF00FF00FF
        v2 = 0x0000FFFF0000FFFF

        x = bitboard
        x = ((x >> 1) & h1) | ((x & h1) << 1)
        x = ((x >> 2) & h2) | ((x & h2) << 2)
        x = ((x >> 4) & h4) | ((x & h4) << 4)
        x = ((x >> 8) & v1) | ((x & v1) << 8)
        x = ((x >> 16) & v2) | ((x & v2) << 16)
        x = (x >> 32) | (x << 32)
        return x & 0xFFFFFFFFFFFFFFFF

    def flipAllBoards(self):
        self.bitboards = [self.flip_bitboard(bitboard) for bitboard in self.bitboards]
        self.bitboards[PieceType.WHITE.value], self.bitboards[PieceType.BLACK.value] = \
            self.bitboards[PieceType.BLACK.value], self.bitboards[PieceType.WHITE.value]
        
    def minimax(self, depth: int, maximizingPlayer: bool):
        if depth == 0 or self.gameState == 0:
            return self.evaluate()

        value = -inf if maximizingPlayer else inf
        legalMoves = self.generateAllLegalMoves()

        for move in legalMoves:
            self.makeMove(move[0], move[1])
            self.flipAllBoards()
            newValue = self.minimax(depth - 1, not maximizingPlayer)
            self.undoMove()
            value = max(value, newValue) if maximizingPlayer else min(
                value, newValue)

        return value

    def negamax(self, depth: int, alpha, beta) -> tuple[float, list]:
        if depth == 0 or self.gameState != 0:
            return self.evaluate(), None

        max_value = -inf
        best_move = None

        for move in self.generateAllLegalMoves():
            searchBoard = deepcopy(self)
            searchBoard.makeMove(move[0], move[1])
            searchBoard.flipAllBoards()
            value, _ = searchBoard.negamax(depth - 1, -beta, -alpha)
            value = -value

            if value > max_value:
                max_value = value
                best_move = move

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return max_value, best_move
