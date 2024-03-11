from evaluation_functions import EvaluationFunction
import numpy as np


class TranspositionTable:  # Class for storing previously evaluated positions to save on computations at higher depths
    def __init__(self):
        self.table = (
            {}
        )  # Initialises a dictionary to store the hashed key and depth and evaluation

    def lookup(
        self, key
    ):  # Method to fetch the data related to the unique hash of the position
        return self.table.get(key)

    def store(
        self, key, score, depth
    ):  # Stores an evaluated position in the dictionary with relevant information
        self.table[key] = {"score": score, "depth": depth}


class ZobristHash:  # Hashing algorithm to uniquely hash a ChessBoard objects's array of 13 bitboards
    def __init__(self, shape=(13,)):
        self.keys = np.random.randint(
            2**64, size=shape, dtype=np.uint64
        )  # Assigns each bitboard a random integer

    def generate_key(self, position):  # Hashes the array of bitboards to a unique key
        return np.bitwise_xor.reduce(position * self.keys)


# Initialises an object of each class for future use
transposition_table = TranspositionTable()
eval = EvaluationFunction()
hash = ZobristHash()


def minimax(board, depth, maximizing_player):
    if depth == 0 or board.is_game_over():
        return None, eval.evaluate(board)

    if maximizing_player:
        best_move = None
        max_eval = -float("inf")

        for move in board.generate_legal_moves():
            board.make_move(move)

            _, eval = minimax(board, depth - 1, False)
            eval = -eval

            board.undo_move()

            if eval > max_eval:
                max_eval = eval
                best_move = move

        return best_move, max_eval
    else:
        best_move = None
        min_eval = float("inf")

        for move in board.generate_legal_moves():
            board.make_move(move)

            _, eval = minimax(board, depth - 1, True)
            eval = -eval

            board.undo_move()

            if eval < min_eval:
                min_eval = eval
                best_move = move

        return best_move, min_eval


def minimax_alpha_beta(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return None, eval.evaluate(board)

    if maximizing_player:
        best_move = None
        max_eval = -float("inf")

        for move in board.generate_legal_moves():
            board.make_move(move)

            _, eval = minimax_alpha_beta(board, depth - 1, alpha, beta, False)
            eval = -eval

            board.undo_move()

            if eval > max_eval:
                max_eval = eval
                best_move = move

            alpha = max(alpha, eval)
            if beta <= alpha:
                break

        return best_move, max_eval
    else:
        best_move = None
        min_eval = float("inf")

        for move in board.generate_legal_moves():
            board.make_move(move)

            _, eval = minimax_alpha_beta(board, depth - 1, alpha, beta, True)
            eval = -eval

            board.undo_move()

            if eval < min_eval:
                min_eval = eval
                best_move = move

            beta = min(beta, eval)
            if beta <= alpha:
                break

        return best_move, min_eval


def negamax(board, depth, color):
    if depth == 0 or board.is_game_over():
        return None, color * eval.evaluate(board)

    best_move = None
    max_score = -float("inf")

    for move in board.generate_legal_moves():
        board.make_move(move)

        _, score = negamax(board, depth - 1, -color)
        score = -score
        board.undo_move()

        if score > max_score:
            max_score = score
            best_move = move

    return best_move, max_score


def negamax_alpha_beta_top(
    board, depth, alpha, beta, color
):  # Negamax split into two functions to save memory by not storing the best move at every recursion call, but only at the top level
    key = hash.generate_key(
        board.all_bitboards
    )  # Generate a unique key for the current position

    if board.is_game_over()[0]:  # If the game is over before the final depth is reached
        print(
            "White won" if board.is_game_over()[1] > 0 else "Black won"
        )  # Check the second argument which indicates who won
        depth = 0  # Resets the depth to trigger the next selection statement

    if depth == 0:  # If the final depth has been reached
        return None, color * eval.evaluate(
            board
        )  # No static best move function so just returns evaluation

    # Initialise variables to starting values
    best_move = None
    best_score = -float("inf")

    # Loop through all the legal moves in the current position
    for move in board.generate_legal_moves():
        board.make_move(move)  # Make the current iterated move
        score = -negamax_alpha_beta(
            board, depth - 1, -beta, -alpha, color
        )  # Call the function from the other colour's perspective, with negative values to represent this
        board.undo_move()  # Undo the move, to prepare the board for the next move in the loop to be made

        if (
            score > best_score
        ):  # If it has found a move which produces a better evaluation
            best_score = score  # Replace the best score with this newly found score
            best_move = move  #  Replace the best move with this newly found move

        # Alpha-beta pruning
        alpha = max(
            alpha, score
        )  # Makes alpha the biggest value out of alpha and score

        if alpha >= beta:  # If the beta cut-off is reached
            break  # Stop searching this branch

    transposition_table.store(
        key, best_score, depth
    )  # Store the evaluated position in the transposition table
    return (
        best_move,
        best_score,
    )  # Return the best move to be played and the associated evaluation of the position


def negamax_alpha_beta(
    board, depth, alpha, beta, color
):  # For recursion calls of negamax
    key = hash.generate_key(
        board.all_bitboards
    )  # Generate a unique key for the current position
    if (
        key in transposition_table.table
        and transposition_table.table[key]["depth"]
        >= depth  # Checks if the current position has already been searched at an equal or greater depth
    ):
        return transposition_table.table[key][
            "score"
        ]  # Return the previously computed evaluation for the position

    if (
        depth == 0 or board.is_game_over()[0]
    ):  # If no more searching for this branch is needed
        return color * eval.evaluate(board)

    best_score = -float("inf")  # Initialise the starting score for this search branch

    # Search through each legal move in the position
    for move in board.generate_legal_moves():
        board.make_move(move)  # Make the move to be searched through
        score = -negamax_alpha_beta(
            board, depth - 1, -beta, -alpha, color
        )  # Call the function with a decremented depth and from the other colour's perspective
        board.undo_move()  # Undo the move

        best_score = max(best_score, score)  # Update the max score

        # Alpha-beta pruning
        alpha = max(alpha, score)  # Update the alpha value

        if alpha >= beta:  # Trigger the beta cut-off
            break  # Stop searching

    transposition_table.store(
        key, best_score, depth
    )  # Store the searched position in the transposition table with relevant data
    return best_score  # Return the best score for this branch of the position


class Node:
    def __init__(self, state):
        self.state = state
        self.children = {}  # Dictionary to store child nodes indexed by actions
        self.visits = 0
        self.reward = 0


def select(node):
    # Implement UCB to select a child node based on the current node's children
    # Recursively call select on the selected child node until a leaf node is reached
    pass


def expand(node):
    # Generate legal moves for the current board state
    legal_moves = node.state.generate_legal_moves()

    # Add child nodes for unexplored moves
    for move in legal_moves:
        if move not in node.children:
            new_state = node.state.make_move(
                move
            )  # Apply the move to create a new state
            node.children[move] = Node(new_state)
    return node.children[move]


def simulate(node):
    # Simulate a game from the current board state until a terminal state is reached
    # Use a simulation policy (e.g., random moves) to determine actions in non-terminal states
    pass


def backpropagate(node, reward):
    # Update the visit count and reward of all nodes traversed from the selected node to the root node
    while node is not None:
        node.visits += 1
        node.reward += reward
        node = node.parent  # Move to the parent node


def monte_carlo(root):
    # Select the action with the highest expected reward based on the visit counts of child nodes of the root node
    best_action = max(
        root.children,
        key=lambda action: root.children[action].reward / root.children[action].visits,
    )
    return best_action
