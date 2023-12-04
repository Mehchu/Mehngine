from fenConversion import fenToBinaryArray
import re
# TODO: Has white starting at 64, try to invert?
# Implement Knight and King movement
# Implement en passant
# Implement castling
# Implement function to flip the board
# Implement function to actually make a move from a board of possible moves
# Implement square on board function
# Board evaluation function
# Array of legal posiitions function
# generateAttackPattern needs to take into account the colour of the piece
#
#
#
STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
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
               '1000001' : 'K'}

pieceValue = {'P' : 1,
              'N' : 3,
              'B' : 3,
              'R' : 5,
              'Q' : 9
              }
class Board:
    def __init__(self, fen):
        self.bitboards = fenToBinaryArray(fen)

    def __repr__(self) -> str:
        stringToPrint = ''

        for board in self.bitboards:
            stringToPrint += printBitboard(board) + '\n\n'
        return stringToPrint
    
    def evaluate(self, depth : int) -> float:
        eval = 0.0
        while depth > 0:
            pass
        for piece in range(64):
            pass
        
        return eval

    def generateWhite(self) -> int:
        return self.generateOccupancyMask() & self.bitboards[WHITE]
    
    def generateBlack(self) -> int:
        return self.generateOccupancyMask() & self.bitboards[BLACK]
    
    def generateOccupancyMask(self) -> int:
        occupancyMask = self.bitboards[0]
        for bitboard in self.bitboards[1:]:
            occupancyMask |= bitboard

        return occupancyMask
    
    
    def determinePieceOnSquare(self, square : int) -> str:
        binString = ''
        for bitboard in self.bitboards:
            binString += '1' if bitboard & 2 ** square != 0 else '0'
        return codedPieces[binString]
        
    def generateMoves(self) -> list:
        occupancyMask = self.generateOccupancyMask()
        arrayOfMoves = []
        whitePieces = self.generateWhite()
        blackPieces = self.generateBlack()
        for square in range(64):
            if 2 ** square & whitePieces != 0:
                piece = self.determinePieceOnSquare(square)
                arrayOfMoves.append(generateAttackPattern(occupancyMask, whitePieces, blackPieces, square, piece))
                
        return arrayOfMoves
                
    
    
def generateAttackPattern(occupancyMask : int, whitePieces : int, blackPieces : int, square : int, piece : str) -> int:
    attackPattern = 0
    match piece.upper():
        case 'K':
            return generateKingMoves(whitePieces, square)
        case 'Q':
            return generateOrthogonalMoves(occupancyMask, square) | generateDiagnonalMoves(occupancyMask, square)
        case 'R':
            return generateOrthogonalMoves(occupancyMask, whitePieces, square)
        case 'B':
            return generateDiagnonalMoves(occupancyMask, whitePieces, square)
        case 'N':
            return generateKnightMoves(whitePieces, square)
        case 'P':
            return generatePawnMoves(occupancyMask, blackPieces, square)
    return attackPattern
    
    
def generateKingMoves(whitePieces : int, square : int):
    attackPattern = 0
    offsets = [-9, -8, -7, -1, 1, 7, 8, 9]
    
    for offset in offsets:
        newSquare = square + offset
        if issquareOnBoard(newSquare) and 2 ** (newSquare) & whitePieces == 0:
            attackPattern += 2 ** (square + offset)
    
    return attackPattern
    
def generateKnightMoves(whitePieces : int, square : int):
    attackPattern = 0
    offsets = [-17, -15, -10, -6, 6, 10, 15, 17]
    
    for offset in offsets:
        newSquare = square + offset
        if issquareOnBoard(newSquare) and 2 ** (newSquare) & whitePieces == 0:
            attackPattern += 2 ** (square + offset)
    
    return attackPattern

def generateOrthogonalMoves(occupancyMask : int, whitePieces : int, square : int) -> int:
    attackPattern = 0
    
    newSquare = square
    for _ in FILES:
        newSquare += 1
        if not issquareOnBoard(newSquare) or 2 ** newSquare & whitePieces != 0 or getRank(square) != getRank(newSquare):
            break
        
        attackPattern += 2 ** newSquare
        
        if 2 ** newSquare & occupancyMask != 0:
            break
            
    newSquare = square
    for _ in FILES:
        newSquare -= 1
        if not issquareOnBoard(newSquare) or 2 ** newSquare & whitePieces != 0 or getRank(square) != getRank(newSquare):
            break
        
        attackPattern += 2 ** newSquare
        
        if 2 ** newSquare & occupancyMask != 0:
            break
    
    newSquare = square
    for _ in RANKS:
        newSquare += 8
        if not issquareOnBoard(newSquare) or 2 ** newSquare & whitePieces != 0 or getFile(square) != getFile(newSquare):
            break
        
        attackPattern += 2 ** newSquare
        
        if 2 ** newSquare & occupancyMask != 0:
            break
            
    newSquare = square
    for _ in RANKS:
        newSquare -= 8
        if not issquareOnBoard(newSquare) or 2 ** newSquare & whitePieces != 0 or getFile(square) != getFile(newSquare):
            break
        
        attackPattern += 2 ** newSquare
        
        if 2 ** newSquare & occupancyMask != 0:
            break
    
    return attackPattern

def generateDiagnonalMoves(occupancyMask : int, whitePices : int, square : int) -> int:
    attackPattern = 0
    # OR parallel to the a1 to h8 diagonal
    newSquare = square
    for _ in RANKS:
        newSquare += 9
        
        if 2 ** newSquare & whitePices != 0:
            break
        
        if abs(getFile(newSquare) - getFile(square)) == abs(getRank(newSquare) - getRank(square)) and issquareOnBoard(newSquare): # No teleporting nonesense
            attackPattern += 2 ** newSquare
            
        if 2 ** newSquare & occupancyMask != 0:
            break
            
    # Other direction
    newSquare = square
    for _ in RANKS:
        newSquare -= 9
        
        if 2 ** newSquare & whitePices != 0:
            break
        
        if abs(getFile(newSquare) - getFile(square)) == abs(getRank(newSquare) - getRank(square)) and issquareOnBoard(newSquare): # No teleporting nonesense
            attackPattern += 2 ** newSquare
            
        if 2 ** newSquare & occupancyMask != 0:
            break
        
    # OR parallel to the h1 to a8 diagonal      
    newSquare = square
    for _ in RANKS:
        newSquare += 7
        
        if 2 ** newSquare & whitePices != 0:
            break
        
        if abs(getFile(newSquare) - getFile(square)) == abs(getRank(newSquare) - getRank(square)) and issquareOnBoard(newSquare): # No teleporting nonesense
            attackPattern += 2 ** newSquare
            
        if 2 ** newSquare & occupancyMask != 0:
            break
            
    # Other direction on other diagonal
    newSquare = square
    for _ in RANKS:
        newSquare -= 7
        
        if 2 ** newSquare & whitePices != 0:
            break
        
        if abs(getFile(newSquare) - getFile(square)) == abs(getRank(newSquare) - getRank(square)) and issquareOnBoard(newSquare): # No teleporting nonesense
            attackPattern += 2 ** newSquare
            
        if 2 ** newSquare & occupancyMask != 0:
            break
        
    return attackPattern
      
def generatePawnMoves(ocuupancyMask : int, blackPieces : int, square : int) -> int:
    attackPattern = 0
    # Find forward pawn moves
    if 2 ** (square - 8) & ocuupancyMask == 0 and issquareOnBoard(square - 8):
        attackPattern += 2 ** (square - 8)
        if getRank(square) == 6:
            attackPattern += 2 ** (square - 16)

    # Find captures
    if 2 ** (square - 7) & blackPieces != 0:
        attackPattern += 2 ** (square - 7)

    if 2 ** (square - 9) & blackPieces != 0:
        attackPattern += 2 ** (square - 9)
    
    return attackPattern
            
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

def issquareOnBoard(square : int) -> bool:
    return 0 <= square <= 63
        
    
board1 = Board('8/8/PPPPPPPP/4B3/pppppppp/8/8/8')
for bitboard in board1.generateMoves():
    print(printBitboard(bitboard))
