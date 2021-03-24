import chess

from search import search

PIECES = {chess.PAWN : 100, chess.KNIGHT : 300, chess.BISHOP : 300, chess.ROOK : 500, chess.QUEEN : 900}

def material_count(board):
    """ Calculates material balance of position using the standard centipawn values of
    Pawn = 1
    Knight & Bishop = 3
    Rook = 5
    Queen = 9
    From the pov of the player whose turn it is
    """
    material = 0
    for piece in PIECES:
        material += PIECES[piece] * len(board.pieces(piece, board.turn))
        material -= PIECES[piece] * len(board.pieces(piece, not board.turn))
    return material

if __name__ == '__main__':
    board = chess.Board(fen='rnbqkbnr/pp2pppp/8/2pP4/3P4/8/PPP2PPP/RNBQKBNR b KQkq - 0 3')
    print(search(material_count, board, 5))