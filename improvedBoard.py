from math import inf
from bitBoardManipulation import *
from fenManipulation import fenToBinaryArray, fenToArray


class Board:
    def __init__(self, fen : str) -> None:
        self.gameState = 0
        
        self.bitboards = fenToBinaryArray(fen) # Converts the initial fen into an array of bitboards
        self.previous_position = fenToBinaryArray(fen)

        self.numberOfBitboards = 7 # Stores number of bitboards for later use
        
        # For converting a binary string from the bitboards into a readable piece
        self.binaryToPiece = {'1010000' : 'P',
                            '1001000' : 'N',
                            '1000100' : 'B',
                            '1000010' : 'R',
                            '1000110' : 'Q',
                            '1000001' : 'K',
                            '0110000' : 'p',
                            '0101000' : 'n',
                            '0100100' : 'b',
                            '0100010' : 'r',
                            '0100110' : 'q',
                            '0100001' : 'k'}
        
        self.WHITE = 0
        self.BLACK = 1
        self.PAWNS = 2
        self.KNIGHTS = 3
        self.DIAGONALS = 4
        self.ORTHOGONALS = 5
        self.KINGS = 6
        
        self.RANKS = range(8)
        self.FILES = range(8)
        
        self.bitboardConversion = {'P' : self.PAWNS,
                                'N' : self.KNIGHTS,
                                'B' : self.DIAGONALS,
                                'R' : self.ORTHOGONALS,
                                'K' : self.KINGS
                                }
        
        self.pieceValue = {'P' : 1,
                        'N' : 3,
                        'B' : 3,
                        'R' : 5,
                        'Q' : 9,
                        'p' : -1,
                        'n' : -3,
                        'b' : -3,
                        'r' : -5,
                        'q' : -9
                        }
        
    def __repr__(self) -> str:
        fen = "/".join(self.rank_to_fen(rank) for rank in range(8))
        return fen

    def rank_to_fen(self, rank: int) -> str:
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
    
    def makeMove(self, startSquare : int, targetSquare : int): # Change order, make efficient?
        self.previous_position = self.bitboards.copy()
        piece = self.determinePieceOnSquare(startSquare) # Determine piece that is moving
        
        if piece == -1: # Blank space means invalid move
            raise ValueError(f"{startSquare} is a blank square and therefore should not be able to make a move")
        
        if piece == piece.lower():
            raise ValueError(f"{startSquare} is a black piece and therefore should not be able to make a move")
        
        self.bitboards[self.WHITE] &= ~(1 << startSquare) # Removes white piece from starting square
        self.bitboards[self.WHITE] |= 1 << targetSquare # Places white piece on target square
        
        for bitboard in range(self.numberOfBitboards - 1): # Remove all target square data
            self.bitboards[bitboard + 1] &= ~(1 << targetSquare)
        
        if piece == 'Q':
                self.bitboards[self.ORTHOGONALS] &= ~(1 << startSquare)
                self.bitboards[self.ORTHOGONALS] |= 1 << targetSquare
                
                
                self.bitboards[self.DIAGONALS] &= ~(1 << startSquare)
                self.bitboards[self.DIAGONALS] |= 1 << targetSquare
                
                return

        self.bitboards[self.bitboardConversion[piece]] &= ~(1 << startSquare)
        self.bitboards[self.bitboardConversion[piece]] |= 1 << targetSquare
        
        
    def undoMove(self):
        self.bitboards = self.previous_position.copy()
        
    def determinePieceOnSquare(self, square : int) -> str:
        binString = ''.join(
            '1' if bitboard & 1 << square != 0 else '0'
            for bitboard in self.bitboards
        )
        if binString == '0' * self.numberOfBitboards: # If an empty square
            return ' '

        return self.binaryToPiece[binString] # Convert the binary string to a piece character
    
    def generateOccupancyMask(self) -> int: # Bitwise OR each bitboard together to return mask of all pieces without any piece data
        occupancyMask = 0
        
        for bitboard in self.bitboards: 
            occupancyMask |= bitboard

        return occupancyMask
    
    def generateWhite(self) -> int:
        return self.generateOccupancyMask() & self.bitboards[self.WHITE]
    
    def generateBlack(self) -> int:
        return self.generateOccupancyMask() & self.bitboards[self.BLACK]
    
    def generateKingMoves(self, whitePieces : int, square : int) -> int:
        kingMoves = 0
        offsets = [-9, -8, -7, -1, 1, 7, 8, 9]
        
        for offset in offsets:
            newSquare = square + offset
            if isSquareOnBoard(newSquare) and 1 << (newSquare) & whitePieces == 0:
                kingMoves += 1 << (square + offset)
                
        return kingMoves
                
    def generatePawnMoves(self, ocuupancyMask : int, blackPieces : int, square : int) -> int:
        pawnMoves = 0
        # Find forward pawn moves
        if 1 << (square - 8) & ocuupancyMask == 0 and isSquareOnBoard(square - 8):
            pawnMoves |= 1 << (square - 8)
            
            if getRank(square) == 6: # If the pawn is still on starting rank
                pawnMoves |= 1 << (square - 16)

        # Find captures
        if 1 << (square - 7) & blackPieces != 0:
            pawnMoves |= 1 << (square - 7)

        if 1 << (square - 9) & blackPieces != 0:
            pawnMoves |= 1 << (square - 9)
        
        return pawnMoves
    
    def generateKnightMoves(self, whitePieces : int, square : int):
        knightMoves = 0
        offsets = [-17, -15, -10, -6, 6, 10, 15, 17]
        
        for offset in offsets:
            newSquare = square + offset
            if isSquareOnBoard(newSquare) and 1 << (newSquare) & whitePieces == 0 and abs(getFile(newSquare) - getFile(square)) <= 2:
                knightMoves += 1 << (square + offset)
        
        return knightMoves
    
    def generateDiagnonalMoves(self, occupancyMask : int, whitePieces : int, square : int) -> int:
        diagnonalMoves = 0
        # OR parallel to the a1 to h8 diagonal
        newSquare = square
        while isSquareOnBoard(newSquare + 9):
            newSquare += 9
            
            if 1 << newSquare & whitePieces != 0:
                break
            
            if abs(getFile(newSquare) - getFile(square)) == abs(getRank(newSquare) - getRank(square)) and isSquareOnBoard(newSquare): # No teleporting nonesense
                diagnonalMoves |= 1 << newSquare
                
            if 1 << newSquare & occupancyMask != 0:
                break
                
        # Other direction
        newSquare = square
        while isSquareOnBoard(newSquare - 9):
            newSquare -= 9
            
            if 1 << newSquare & whitePieces != 0:
                break
            
            if abs(getFile(newSquare) - getFile(square)) == abs(getRank(newSquare) - getRank(square)) and isSquareOnBoard(newSquare): # No teleporting nonesense
                diagnonalMoves |= 1 << newSquare
                
            if 1 << newSquare & occupancyMask != 0:
                break
            
        # OR parallel to the h1 to a8 diagonal      
        newSquare = square
        while isSquareOnBoard(newSquare + 7):
            newSquare += 7
            
            if 1 << newSquare & whitePieces != 0:
                break
            
            if abs(getFile(newSquare) - getFile(square)) == abs(getRank(newSquare) - getRank(square)) and isSquareOnBoard(newSquare): # No teleporting nonesense
                diagnonalMoves |= 1 << newSquare
                
            if 1 << newSquare & occupancyMask != 0:
                break
                
        # Other direction on other diagonal
        newSquare = square
        while isSquareOnBoard(newSquare - 7):
            newSquare -= 7
            
            if 1 << newSquare & whitePieces != 0:
                break
            
            if abs(getFile(newSquare) - getFile(square)) == abs(getRank(newSquare) - getRank(square)) and isSquareOnBoard(newSquare): # No teleporting nonesense
                diagnonalMoves |= 1 << newSquare
                
            if 1 << newSquare & occupancyMask != 0:
                break
            
        return diagnonalMoves
        
    def generateOrthogonalMoves(self, occupancyMask : int, whitePieces : int, square : int) -> int:
        orthogonalMoves = 0
        
        newSquare = square
        for _ in self.FILES:
            newSquare += 1
            if not isSquareOnBoard(newSquare) or 1 << newSquare & whitePieces != 0 or getRank(square) != getRank(newSquare):
                break
            
            orthogonalMoves |= 1 << newSquare
            
            if 1 << newSquare & occupancyMask != 0:
                break
                
        newSquare = square
        for _ in self.FILES:
            newSquare -= 1
            if not isSquareOnBoard(newSquare) or 1 << newSquare & whitePieces != 0 or getRank(square) != getRank(newSquare):
                break
            
            orthogonalMoves |= 1 << newSquare
            
            if 1 << newSquare & occupancyMask != 0:
                break
        
        newSquare = square
        for _ in self.RANKS:
            newSquare += 8
            if not isSquareOnBoard(newSquare) or 1 << newSquare & whitePieces != 0 or getFile(square) != getFile(newSquare):
                break
            
            orthogonalMoves |= 1 << newSquare
            
            if 1 << newSquare & occupancyMask != 0:
                break
                
        newSquare = square
        for _ in self.RANKS:
            newSquare -= 8
            if not isSquareOnBoard(newSquare) or 1 << newSquare & whitePieces != 0 or getFile(square) != getFile(newSquare):
                break
            
            orthogonalMoves |= 1 << newSquare
            
            if 1 << newSquare & occupancyMask != 0:
                break
        
        return orthogonalMoves
    
    def generatePieceMoves(self, square : int) -> list:
        moves = 0
        
        occupancyMask = self.generateOccupancyMask()
        whitePieces = self.generateWhite()
        blackPieces = self.generateBlack()
        piece = self.determinePieceOnSquare(square)
        
        match piece:
            case 'K':
                moves = self.generateKingMoves(whitePieces, square)
            case 'Q':
                moves = self.generateOrthogonalMoves(occupancyMask, whitePieces, square) | self.generateDiagnonalMoves(occupancyMask, whitePieces, square)
            case 'R':
                moves = self.generateOrthogonalMoves(occupancyMask, whitePieces, square)
            case 'B':
                moves = self.generateDiagnonalMoves(occupancyMask, whitePieces, square)
            case 'N':
                moves = self.generateKnightMoves(whitePieces, square)
            case 'P':
                moves = self.generatePawnMoves(occupancyMask, blackPieces, square) # Make use white pieces maybe?

        return self.turnPieceMovesIntoPairsOfMoves(square, moves)
    
    def turnPieceMovesIntoPairsOfMoves(self, startSquare, moves) -> list:
        return [
            [startSquare, square]
            for square in range(64)
            if 1 << square & moves != 0
        ]
    
    def generateAllLegalMoves(self) -> list:
        pairedMoves = []

        for square in range(64):
            if 1 << square & self.generateWhite() != 0:
                pairedMove = self.generatePieceMoves(square)

                if pairedMove != []:
                    pairedMoves.extend(iter(pairedMove))
        return pairedMoves
    
    def evaluate(self) -> float: # Maybe seperate out to remove best_move from each call?
        eval = 0.0
        whitePieces = self.generateWhite()
        blackPieces = self.generateBlack()
        
        for square in range(64):
            piece = self.determinePieceOnSquare(square)
            
            if piece == -1:
                continue
            
            if piece.upper() == 'K':
                continue
            
            if 1 << square & whitePieces != 0:
                eval += self.pieceValue[piece]
            
            if 1 << square & blackPieces != 0:
                eval += self.pieceValue[piece]
            
        return eval
    
    def flipAllBoards(self):
        h1 = 0x5555555555555555
        h2 = 0x3333333333333333
        h4 = 0x0F0F0F0F0F0F0F0F
        v1 = 0x00FF00FF00FF00FF
        v2 = 0x0000FFFF0000FFFF
        
        for i in range(self.numberOfBitboards):
            x = self.bitboards[i]

            x = ((x >> 1) & h1) | ((x & h1) << 1)
            x = ((x >> 2) & h2) | ((x & h2) << 2)
            x = ((x >> 4) & h4) | ((x & h4) << 4)
            x = ((x >> 8) & v1) | ((x & v1) << 8)
            x = ((x >> 16) & v2) | ((x & v2) << 16)
            x = (x >> 32) | (x << 32)

        # Ensure that the result is a 64-bit unsigned integer
            self.bitboards[i] = x & 0xFFFFFFFFFFFFFFFF
            
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
            value = max(value, newValue) if maximizingPlayer else min(value, newValue)

        return value
        
    def negamax(self, depth: int) -> float:
        if depth == 0:
            return self.evaluate()
        max_value = -inf

        for move in self.generateAllLegalMoves():
            self.makeMove(move[0], move[1])
            self.flipAllBoards()
            value = self.negamax(depth - 1)
            self.undoMove()
            max_value = max(max_value, value)

        return max_value