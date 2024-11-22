import random

class AI:
    def get_move(self, board):
        return random.choice(list(board.board.legal_moves))
