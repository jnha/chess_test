import chess

def sign(b: bool):
    return 2*b-1

def null_eval(board):
    return 0
    
RESULT = {'1-0': 9999, '0-1': -9999, '1/2-1/2': 0}

def search(eval, board, depth, best_line, best=-9999, limit=9999):
    """ Alpha-beta search (fail-hard) """
    if board.is_game_over():
        return sign(board.turn)*RESULT[board.result()]
    if depth == 0:
        return eval(board)
    for d in range(1, depth):
        best_score = -10000
        best_move = chess.Move.null
        for move in moves:
            board.push(move)
            score = search(eval, board, depth-1, best_line, -limit, -best)
            board.pop()
            if score >= limit:
                return limit
            if score > best:
                best = score
                line.append(move)
                best_line = line
    return best, best_line

if __name__ == '__main__':
    board = chess.Board()
    print(iterative_deepening(null_eval, board, 6))