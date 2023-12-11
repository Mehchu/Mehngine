from fenManipulation import fenToBinaryArray
import re
from math import inf
# TODO: Has white starting at 64, try to invert?
# Implement Knight and King movement
# Implement en passant
# Implement castling
# Implement promotion
# Implement function to flip the board
# Implement function to actually make a move from a board of possible moves
# Implement square on board function
# Board evaluation function
# Array of legal posiitions function
# generateMoves needs to take into account the colour of the piece
#
#
#
STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
WHITE_WON = 1
NUMBER_OF_BITBOARDS = 7
WHITE = 0
BLACK = 1
PAWNS = 2
KNIGHTS = 3
DIAGONALS = 4
ORTHOGONALS = 5
KINGS = 6

FILES, RANKS = range(8), range(8)
# Only care about moves from white (flip board to act as black?)
codedPieces = {'1010000' : 'P',
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

pieceValue = {'P' : 1,
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

bitboardConversion = {'P' : PAWNS,
              'N' : KNIGHTS,
              'B' : DIAGONALS,
              'R' : ORTHOGONALS,
              'K' : KINGS
              }

class Board:
    def __init__(self, fen):
        self.bitboards = fenToBinaryArray(fen)
        self.state = -1

    def __repr__(self) -> str:
        stringToPrint = ''

        for board in self.bitboards:
            stringToPrint += printBitboard(board) + '\n\n'
        return stringToPrint
    
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
            
            if 2 ** square & whitePieces != 0:
                eval += pieceValue[piece]
            
            if 2 ** square & blackPieces != 0:
                eval += pieceValue[piece]
            
        return eval
    
    def minimax(self, depth : int, maximizingPlayer : bool):
        searchBoard = self
        move = []
        if depth == 0 or searchBoard.state != -1:
            return searchBoard.evaluate()
        
        if maximizingPlayer:
            print("First")
            value = -inf
            
            for i in range(NUMBER_OF_BITBOARDS):
                searchBoard.bitboards[i] = flipBoard(searchBoard.bitboards[i])
            
                
            for move in searchBoard.generateAllLegalMoves():
                
                print("Mask")
                print(printBitboard(searchBoard.generateOccupancyMask()))
                
                print(move)
                
                searchBoard.makeMove(move[0], move[1])
                value = max(value, searchBoard.minimax(depth - 1, False))
                
            
            return value
                
        else:
            print("Second")
            value = inf
            
            for i in range(NUMBER_OF_BITBOARDS): # Make into method for class?
                searchBoard.bitboards[i] = flipBoard(searchBoard.bitboards[i])
            
            
            for move in searchBoard.generateAllLegalMoves():
                print("Mask")
                print(printBitboard(searchBoard.generateOccupancyMask()))
                
                print(move)
                
                searchBoard.makeMove(move[0], move[1])
                value = min(value, searchBoard.minimax(depth - 1, True))
                
            return value
        
    def makeMove(self, startSquare : int, targetSquare : int): # Change order, make efficient?
        piece = self.determinePieceOnSquare(startSquare)
        
        if piece == -1:
            return
        
        piece = piece.upper()
        
        self.bitboards[WHITE] &= ~(2 ** startSquare)
        self.bitboards[WHITE] |= 2 ** targetSquare
        
        self.bitboards[BLACK] &= ~(2 ** targetSquare)
        
        if (opponentPiece := self.determinePieceOnSquare(targetSquare)) != -1:
            opponentPiece = opponentPiece.upper()

            if opponentPiece == 'q':
                self.bitboards[ORTHOGONALS] &= ~(2 ** startSquare)
                self.bitboards[ORTHOGONALS] |= 2 ** targetSquare
                
                
                self.bitboards[DIAGONALS] &= ~(2 ** startSquare)
                self.bitboards[DIAGONALS] |= 2 ** targetSquare
                
                return
            
            self.bitboards[bitboardConversion[opponentPiece]] &= ~(2 ** targetSquare)
        

        
        if piece == 'Q':
                self.bitboards[ORTHOGONALS] &= ~(2 ** startSquare)
                self.bitboards[ORTHOGONALS] |= 2 ** targetSquare
                
                
                self.bitboards[DIAGONALS] &= ~(2 ** startSquare)
                self.bitboards[DIAGONALS] |= 2 ** targetSquare
                
                return


        self.bitboards[bitboardConversion[piece]] &= ~(2 ** startSquare)
        self.bitboards[bitboardConversion[piece]] |= 2 ** targetSquare

    def generateWhite(self) -> int:
        return self.generateOccupancyMask() & self.bitboards[WHITE]
    
    def generateBlack(self) -> int:
        return self.generateOccupancyMask() & self.bitboards[BLACK]
    
    def generateOccupancyMask(self) -> int:
        occupancyMask = self.bitboards[0]
        for bitboard in self.bitboards[1:]:
            occupancyMask |= bitboard

        return occupancyMask
    
    def determinePieceOnSquare(self, square : int):
        binString = ''
        for bitboard in self.bitboards:
            binString += '1' if bitboard & 2 ** square != 0 else '0'
            
        if binString == '0' * NUMBER_OF_BITBOARDS:
            return -1
        return codedPieces[binString]
    
    def generateAllLegalMoves(self) -> list:
        pairedMoves = []
        for square in range(64):
            if 2 ** square & self.generateWhite() != 0:
                moves = self.generateLegalMoves(square)
                pairedMove = turnAllMovesIntoPairsOfMoves(square, moves)
                
                if pairedMove != []:
                    for movePerPiece in pairedMove:
                        pairedMoves.append(movePerPiece)

        return pairedMoves
        
    def generateLegalMoves(self, square : int) -> int:
        moves = 0
        
        occupancyMask = self.generateOccupancyMask()
        whitePieces = self.generateWhite()
        blackPieces = self.generateBlack()
        piece = self.determinePieceOnSquare(square)
        
        match piece:
            case 'K':
                return generateKingMoves(whitePieces, square)
            case 'Q':
                return generateOrthogonalMoves(occupancyMask, whitePieces, square) | generateDiagnonalMoves(occupancyMask, whitePieces, square)
            case 'R':
                return generateOrthogonalMoves(occupancyMask, whitePieces, square)
            case 'B':
                return generateDiagnonalMoves(occupancyMask, whitePieces, square)
            case 'N':
                return generateKnightMoves(whitePieces, square)
            case 'P':
                return generatePawnMoves(occupancyMask, blackPieces, square) # Make use white pieces maybe?
        return moves
    
    
def turnAllMovesIntoPairsOfMoves(startSquare, moves):
    pairs = []
    for square in range(64):
        if 2 ** square & moves != 0:
            pairs.append([startSquare, square])
            
    return pairs

def flipBoard(x):
    h1 = 0x5555555555555555
    h2 = 0x3333333333333333
    h4 = 0x0F0F0F0F0F0F0F0F
    v1 = 0x00FF00FF00FF00FF
    v2 = 0x0000FFFF0000FFFF

    x = ((x >> 1) & h1) | ((x & h1) << 1)
    x = ((x >> 2) & h2) | ((x & h2) << 2)
    x = ((x >> 4) & h4) | ((x & h4) << 4)
    x = ((x >> 8) & v1) | ((x & v1) << 8)
    x = ((x >> 16) & v2) | ((x & v2) << 16)
    x = (x >> 32) | (x << 32)

    # Ensure that the result is a 64-bit unsigned integer
    return x & 0xFFFFFFFFFFFFFFFF

def generateKingMoves(whitePieces : int, square : int):
    moves = 0
    offsets = [-9, -8, -7, -1, 1, 7, 8, 9]
    
    for offset in offsets:
        newSquare = square + offset
        if isSquareOnBoard(newSquare) and 2 ** (newSquare) & whitePieces == 0:
            moves += 2 ** (square + offset)
    
    return moves
    
def generateKnightMoves(whitePieces : int, square : int):
    moves = 0
    offsets = [-17, -15, -10, -6, 6, 10, 15, 17]
    
    for offset in offsets:
        newSquare = square + offset
        if isSquareOnBoard(newSquare) and 2 ** (newSquare) & whitePieces == 0:
            moves += 2 ** (square + offset)
    
    return moves

def generateOrthogonalMoves(occupancyMask : int, whitePieces : int, square : int) -> int:
    moves = 0
    
    newSquare = square
    for _ in FILES:
        newSquare += 1
        if not isSquareOnBoard(newSquare) or 2 ** newSquare & whitePieces != 0 or getRank(square) != getRank(newSquare):
            break
        
        moves += 2 ** newSquare
        
        if 2 ** newSquare & occupancyMask != 0:
            break
            
    newSquare = square
    for _ in FILES:
        newSquare -= 1
        if not isSquareOnBoard(newSquare) or 2 ** newSquare & whitePieces != 0 or getRank(square) != getRank(newSquare):
            break
        
        moves += 2 ** newSquare
        
        if 2 ** newSquare & occupancyMask != 0:
            break
    
    newSquare = square
    for _ in RANKS:
        newSquare += 8
        if not isSquareOnBoard(newSquare) or 2 ** newSquare & whitePieces != 0 or getFile(square) != getFile(newSquare):
            break
        
        moves += 2 ** newSquare
        
        if 2 ** newSquare & occupancyMask != 0:
            break
            
    newSquare = square
    for _ in RANKS:
        newSquare -= 8
        if not isSquareOnBoard(newSquare) or 2 ** newSquare & whitePieces != 0 or getFile(square) != getFile(newSquare):
            break
        
        moves += 2 ** newSquare
        
        if 2 ** newSquare & occupancyMask != 0:
            break
    
    return moves

def generateDiagnonalMoves(occupancyMask : int, whitePieces : int, square : int) -> int:
    moves = 0
    # OR parallel to the a1 to h8 diagonal
    newSquare = square
    while isSquareOnBoard(newSquare + 9):
        newSquare += 9
        
        if 2 ** newSquare & whitePieces != 0:
            break
        
        if abs(getFile(newSquare) - getFile(square)) == abs(getRank(newSquare) - getRank(square)) and isSquareOnBoard(newSquare): # No teleporting nonesense
            moves += 2 ** newSquare
            
        if 2 ** newSquare & occupancyMask != 0:
            break
            
    # Other direction
    newSquare = square
    while isSquareOnBoard(newSquare - 9):
        newSquare -= 9
        
        if 2 ** newSquare & whitePieces != 0:
            break
        
        if abs(getFile(newSquare) - getFile(square)) == abs(getRank(newSquare) - getRank(square)) and isSquareOnBoard(newSquare): # No teleporting nonesense
            moves += 2 ** newSquare
            
        if 2 ** newSquare & occupancyMask != 0:
            break
        
    # OR parallel to the h1 to a8 diagonal      
    newSquare = square
    while isSquareOnBoard(newSquare + 7):
        newSquare += 7
        
        if 2 ** newSquare & whitePieces != 0:
            break
        
        if abs(getFile(newSquare) - getFile(square)) == abs(getRank(newSquare) - getRank(square)) and isSquareOnBoard(newSquare): # No teleporting nonesense
            moves += 2 ** newSquare
            
        if 2 ** newSquare & occupancyMask != 0:
            break
            
    # Other direction on other diagonal
    newSquare = square
    while isSquareOnBoard(newSquare - 7):
        newSquare -= 7
        
        if 2 ** newSquare & whitePieces != 0:
            break
        
        if abs(getFile(newSquare) - getFile(square)) == abs(getRank(newSquare) - getRank(square)) and isSquareOnBoard(newSquare): # No teleporting nonesense
            moves += 2 ** newSquare
            
        if 2 ** newSquare & occupancyMask != 0:
            break
        
    return moves
      
def generatePawnMoves(ocuupancyMask : int, blackPieces : int, square : int) -> int:
    moves = 0
    # Find forward pawn moves
    if 2 ** (square + 8) & ocuupancyMask == 0 and isSquareOnBoard(square + 8):
        moves += 2 ** (square + 8)
        if getRank(square) == 6:
            moves += 2 ** (square + 16)

    # Find captures
    if 2 ** (square + 7) & blackPieces != 0:
        moves += 2 ** (square + 7)

    if 2 ** (square + 9) & blackPieces != 0:
        moves += 2 ** (square + 9)
    
    return moves
            
def printBitboard(board : int) -> str:
    binBoard = bin(board)[2:] # Remove the 0b which starts all binary strings
    while len(binBoard) < 64:
        binBoard = '0' + binBoard
    count = 0
    stringToPrint = ""
    for square in binBoard:
        stringToPrint += square + ' '
        count += 1

        if count == 8:
            stringToPrint += '\n'
            count = 0
    
    return stringToPrint

def getFile(square : int) -> int:
    return square % 8

def getRank(square : int) -> int:
    return square // 8

def squareOf(rank : int, file : int) -> int:
    return rank * 8 + file

def isSquareOnBoard(square : int) -> bool:
    return 0 <= square <= 63
        
board1 = Board('8/8/8/2ppp3/2pQp3/2ppp3/8/8')

print(board1.minimax(2, True))
