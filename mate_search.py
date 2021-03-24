import time

import chess

### Alpha beta search, reaches depth 5 (10 ply)
# Faster on positions with a mate than those without a mate

WON_POSITIONS = {} # Transposition table for wins

def is_won(board, depth, forcing=True, check_only=False):
    """ Retuns moves to checkmate if one exists else 0 """
    check = []
    no_check = []
    fen = (board.board_fen(), board.castling_rights, board.ep_square)
    if fen in WON_POSITIONS:
        return WON_POSITIONS[fen]
    for move in board.legal_moves:
        check.append(move) if board.gives_check(move) else no_check.append(move)
    for move in check:
        board.push(move)
        won = is_lost(board, depth-1, forcing, check_only)
        board.pop()
        if won:
            WON_POSITIONS[fen]=won
            return won
    if check_only or depth == 1: # Cannot checkmate on next move unless giving check
        return 0
    for move in no_check:
        if forcing:
            board.push(chess.Move.null())
            mate_threat = is_lost(board, depth-1, forcing, check_only=True)
            board.pop()
            if not mate_threat:
                continue # Skip moves that don't threaten a forcing checkmate
            board.pop()
        board.push(move)
        won = is_lost(board, depth-1, forcing, check_only)
        board.pop()
        if won:
            WON_POSITIONS[fen]=won
            return won
    return 0

ESCAPE_POSITIONS = {} # Transposition table for draws

def is_lost(board, depth, forcing=True, check_only=False):
    """ Returns moves to being checkmated or 0 if no forced mate in depth """
    if board.is_checkmate():
        return 1
    if depth <= 0:
        return 0
    fen = (board.board_fen(), board.castling_rights, board.ep_square)
    if fen in ESCAPE_POSITIONS and ESCAPE_POSITIONS[fen] >= depth:
        return 0
    check = []
    no_check = []
    best = 0
    for move in board.legal_moves:
        check.append(move) if board.gives_check(move) else no_check.append(move)
    moves = check + no_check
    for move in moves:
        board.push(move)
        lost = is_won(board, depth, forcing, check_only)
        board.pop()
        if not lost:
            ESCAPE_POSITIONS[fen] = depth
            return 0
        best = max(best, lost)
    return best + 1


### Proof number search ###
PROOF_LIMIT = 20000
class ProofNode:
    def __init__(self, board, move=None, parent=None):
        self.parent = parent
        self.move = move
        self.children = None
    
    def set_proof_and_disproof_numbers(self):
        raise NotImplementedError()

    def update_ancestors(self, board):
        self.set_proof_and_disproof_numbers()
        node = self.parent
        while node:
            board.pop()
            node.set_proof_and_disproof_numbers()
            node = node.parent

class AndNode(ProofNode):
    """ And node in proof number search tree """
    def __init__(self, board, move=None, parent=None):
        if board.is_game_over():
            if board.is_checkmate():
                self.proof = 0
                self.disproof = PROOF_LIMIT
            else:
                self.proof = PROOF_LIMIT
                self.disproof = 0
        else:
            self.proof = len(list(board.legal_moves))
            self.disproof = 1
        super().__init__(board, move, parent)

    def generate_children(self, board):
        self.children = []
        for move in board.legal_moves:
            board.push(move)
            self.children.append(OrNode(board, move, self))
            board.pop()

    def set_proof_and_disproof_numbers(self):
        if self.children:
            self.proof = sum(n.proof for n in self.children)
            self.disproof = min(n.disproof for n in self.children)

    def select_most_proving(self, board):
        if self.children:
            for child in self.children:
                if child.disproof == self.disproof:
                    board.push(child.move)
                    return child.select_most_proving(board)
            raise RuntimeError("not finding a most proving node isn't supposed to happen")
        return self
                    
class OrNode(ProofNode):
    """ Or node in proof number search tree """
    def __init__(self, board, move=None, parent=None):
        if board.is_game_over():
            self.proof = PROOF_LIMIT
            self.disproof = 0
        else:
            self.proof = 1
            self.disproof = len(list(board.legal_moves))
        super().__init__(board, move, parent)

    def generate_children(self, board):
        self.children = []
        for move in board.legal_moves:
            board.push(move)
            self.children.append(AndNode(board, move, parent=self))
            board.pop()

    def set_proof_and_disproof_numbers(self):
        if self.children:
            self.proof = min(n.proof for n in self.children)
            self.disproof = sum(n.disproof for n in self.children)

    def select_most_proving(self, board):
        if self.children:
            for child in self.children:
                if child.proof == self.proof:
                    board.push(child.move)
                    return child.select_most_proving(board)
            raise RuntimeError("not finding a most proving node isn't supposed to happen")
        return self

def proof_number_search(board):
    root = OrNode(board)
    while root.proof != 0 and root.disproof != 0 and root.proof < PROOF_LIMIT and root.disproof < PROOF_LIMIT:
        most_proving_node = root.select_most_proving(board)
        most_proving_node.generate_children(board)
        most_proving_node.update_ancestors(board)
    if root.proof == 0: return 'win'
    if root.disproof == 0: return 'draw/loss'
    return 'unknown'

if __name__ == '__main__':
    board = chess.Board('r5k1/pb4pp/1p6/2p5/2Pp1P2/3KPN2/P1R3qP/3Q1R2 b - - 0 1')
    for depth in range(1, 8):
        before = time.time()
        print(is_won(board, depth), time.time()-before)
    before = time.time()
    print(proof_number_search(board), time.time()-before)
