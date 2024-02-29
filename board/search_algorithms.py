def minimax(board, depth, maximizing_player):
    if depth == 0 or board.is_game_over():
        return None, board.evaluate()

    if maximizing_player:
        best_move = None
        max_eval = -float("inf")
        for move in board.generateAllLegalMoves():
            board.make_move(move)
            board.flip_board()
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

        for move in board.generateAllLegalMoves():
            board.make_move(move)
            board.flip_board()
            _, eval = minimax(board, depth - 1, True)
            eval = -eval
            board.undo_move()
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return best_move, min_eval


def minimax_alpha_beta(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return None, board.evaluate()

    if maximizing_player:
        best_move = None
        max_eval = -float("inf")

        for move in board.generateAllLegalMoves():
            board.make_move(move)
            board.flip_board()

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

        for move in board.generateAllLegalMoves():
            board.make_move(move)
            board.flip_board()

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
        return color * board.evaluate(), None

    best_move = None
    for move in board.generateAllLegalMoves():
        board.make_move(move)
        board.flip_board()

        score, _ = negamax_alpha_beta(board, depth - 1, -color)
        score = -score
        board.undo_move()

        if score > max_score:
            max_score = score
            best_move = move

    return max_score, best_move


def negamax_alpha_beta(board, depth, alpha, beta, color):
    if depth == 0 or board.is_game_over():
        return color * board.evaluate(), None

    best_move = None
    for move in board.generateAllLegalMoves():
        board.make_move(move)
        board.flip_board()
        score, _ = negamax_alpha_beta(board, depth - 1, -beta, -alpha, -color)
        score = -score
        board.undo_move()

        if score >= beta:
            return beta, best_move

        if score > alpha:
            alpha = score
            best_move = move

    return alpha, best_move
