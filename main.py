from improvedBoard import Board
from fenManipulation import fenToArray
from math import inf

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
TEST_FEN = "rnbqkbnr/ppppp2p/5p2/6p1/4P3/8/PPPP1PPP/RNBQKBNR"
OTHER_TEST_FEN = "3Q4/8/k1K5/8/8/8/8/8"

def main():
    position = Board(OTHER_TEST_FEN)
    
    print(position.negamax(5, -inf, inf)) # Should always be a multiple of two
    
    
    
def printArrays(arrays):
    border = "-" * 26
    print(border)
    for array in arrays:
        print("| " + " ".join(str(element) for element in array) + " |")
    print(border[:-1])
            

if __name__ == "__main__":
    main()





