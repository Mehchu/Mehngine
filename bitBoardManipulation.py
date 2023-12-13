def printBitboard(board : int) -> str:
    binBoard = bin(board)[2:] # Remove the 0b which starts all binary strings

    while len(binBoard) < 64: # Ensure binary is the required 64 bits long to be printed
        binBoard = f'0{binBoard}'

    count = 0
    stringToPrint = ""

    for square in binBoard:
        stringToPrint += f'{square} '
        count += 1

        if count == 8: # Go onto a new line each time a file is filled
            stringToPrint += '\n'
            count = 0

    return stringToPrint

def getFile(square : int) -> int: # Return the index of the file of the square
    return square % 8

def getRank(square : int) -> int: # Return the index of the rank of the square
    return square // 8

def squareOf(rank : int, file : int) -> int: # Return the square on the specified rank and file
    return rank * 8 + file

def isSquareOnBoard(square : int) -> bool: # Returns true if the specified square is a valid square on the board
    return 0 <= square <= 63