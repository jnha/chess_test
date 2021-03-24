import random

from collections import defaultdict

import chess
import chess.pgn

def random_bot(board):
    return random.choice(list(board.legal_moves))

def capture_bot(board):
    moves = [move for move in board.legal_moves if board.is_capture(move)]
    if not moves:
        moves = list(board.legal_moves)
    return random.choice(moves)

def check_bot(board):
    moves = [move for move in board.legal_moves if board.gives_check(move)]
    if not moves:
        moves = list(board.legal_moves)
    return random.choice(moves)

def play_game(white, black, board=None):
    if board is None:
        board = chess.Board()
    while not board.is_game_over():
        board.push(white(board))
        if board.is_game_over():
            break
        board.push(black(board))
    return board

def matchup(white, black, n):
    results = defaultdict(int)
    for i in range(n):
        game = play_game(white, black)
        results[game.result()] += 1
    return dict(results)

if __name__ == '__main__':
    #print(chess.pgn.Game.from_board(play_game(noob_crusher_9000, random_player)))
    print(matchup(capture_bot, check_bot, 100))