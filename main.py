from improvedBoard import Board
from fenManipulation import fenToArray


# TODO: Improve generation of diagonal and orthogonal moves
#
#
#

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
TEST_FEN = "8/8/8/4b3/3B4/8/8/8"

def main():
    position = Board(STARTING_FEN)

    
    print(position.negamax(2))
    
    
    
def printArrays(arrays): # To print the array of the ranks of a board in a readable form
    stringToPrint = "--------------------------\n|"

    for array in arrays:
        for element in array:
            stringToPrint += f' {str(element)} '
        stringToPrint += '|\n|'

    stringToPrint += "------------------------|"
    print(stringToPrint)
            

if __name__ == "__main__":
    main()





