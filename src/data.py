import chess
import pygame
import os
import utils

class GameResource:
    def __init__(self):
        self.sprites_per_row = 6
        self.sprites_per_column = 2

    def load_piece_images(self, square_size):
        pieces = "KQBNRPkqbnrp"  # uppercase: White pieces, lowercase: Black pieces
        
        # load and cut the sprite sheet into individual pieces
        sprite_array = utils.cut_spritesheet(os.path.join("res", "piecies.png"), self.sprites_per_row, self.sprites_per_column)
        
        images = {}
        
        for i, piece in enumerate(pieces):
            images[piece] = sprite_array[i]
            images[piece] = pygame.transform.smoothscale(images[piece], (square_size, square_size))
        
        return images

# Rook directions
ROOK_DIRECTIONS = [-8, 8, -1, 1]

# Bishop directions (diagonals)
BISHOP_DIRECTIONS = [-9, 9, -7, 7]

# Knight moves (in 'L' shape)
KNIGHT_MOVES = [-17, -15, -10, -6, 6, 10, 15, 17]

# King moves (one square in any direction)
KING_MOVES = [-9, -8, -7, -1, 1, 7, 8, 9]

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 100,  
}

POSITIONAL_BONUS = {
    chess.PAWN: [
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 5, 10, 10, 10, 10, 5, 0,
        0, 5, 10, 15, 15, 10, 5, 0,
        0, 5, 10, 20, 20, 10, 5, 0,
        0, 5, 10, 20, 20, 10, 5, 0,
        0, 5, 10, 15, 15, 10, 5, 0,
        0, 5, 10, 10, 10, 10, 5, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    ],
    chess.KNIGHT: [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50
    ],
    chess.BISHOP: [
        -20, -10, 0, 5, 5, 0, -10, -20,
        -10, 0, 5, 10, 10, 5, 0, -10,
        0, 5, 10, 15, 15, 10, 5, 0,
        5, 10, 15, 20, 20, 15, 10, 5,
        5, 10, 15, 20, 20, 15, 10, 5,
        0, 5, 10, 15, 15, 10, 5, 0,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -20, -10, 0, 5, 5, 0, -10, -20
    ],
    chess.ROOK: [
        0, 0, 5, 10, 10, 5, 0, 0,
        0, 5, 10, 15, 15, 10, 5, 0,
        0, 5, 15, 20, 20, 15, 5, 0,
        0, 5, 15, 20, 20, 15, 5, 0,
        0, 5, 15, 20, 20, 15, 5, 0,
        0, 5, 10, 15, 15, 10, 5, 0,
        0, 0, 5, 10, 10, 5, 0, 0,
        0, 0, 5, 10, 10, 5, 0, 0
    ],
    chess.QUEEN: [
        -20, -10, 0, 5, 5, 0, -10, -20,
        -10, 0, 5, 10, 10, 5, 0, -10,
        0, 5, 10, 20, 20, 10, 5, 0,
        5, 10, 20, 30, 30, 20, 10, 5,
        5, 10, 20, 30, 30, 20, 10, 5,
        0, 5, 10, 20, 20, 10, 5, 0,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -20, -10, 0, 5, 5, 0, -10, -20
    ],
    chess.KING: [
        -50, -40, -30, -20, -20, -30, -40, -50,
        -40, -30, -20, 0, 0, -20, -30, -40,
        -30, -20, 0, 10, 10, 0, -20, -30,
        -20, 0, 10, 20, 20, 10, 0, -20,
        -20, 0, 10, 20, 20, 10, 0, -20,
        -30, -20, 0, 10, 10, 0, -20, -30,
        -40, -30, -20, 0, 0, -20, -30, -40,
        -50, -40, -30, -20, -20, -30, -40, -50
    ]
}

# CASTLING_RIGHTS = {
#     chess.WHITE: {
#         "kingside": 1,  # White kingside castling (bit 0)
#         "queenside": 2  # White queenside castling (bit 1)
#     },
#     chess.BLACK: {
#         "kingside": 4,  # Black kingside castling (bit 2)
#         "queenside": 8  # Black queenside castling (bit 3)
#     }
# }

OPENING_BOOK = {
    "startpos": [
        chess.Move.from_uci("e2e4"),  # King's Pawn Opening: 1. e4
        chess.Move.from_uci("e7e5"),  # Black's response: 1... e5
        chess.Move.from_uci("g1f3")   # White develops knight: 2. Nf3
    ],
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": [
        chess.Move.from_uci("e2e4"),  # King's Pawn Opening: 1. e4
        chess.Move.from_uci("e7e5"),  # Black's response: 1... e5
        chess.Move.from_uci("g1f3")   # White develops knight: 2. Nf3
    ],
    "rnbqkbnr/ppp-pppp/8/8/8/8/PPP-PPPP/RNBQKBNR w KQkq - 0 1": [
        chess.Move.from_uci("d2d4"),  # Queen's Pawn Opening: 1. d4
        chess.Move.from_uci("d7d5"),  # Black's response: 1... d5
        chess.Move.from_uci("g1f3")   # White develops knight: 2. Nf3
    ],
    "rnbqkbnr/pp1ppppp/8/8/8/8/PPP1PPPP/RNBQKBNR w KQkq - 0 1": [
        chess.Move.from_uci("e2e4"),  # Sicilian Defense: 1. e4 c5
        chess.Move.from_uci("c7c5"),  # Black's response: 1... c5
        chess.Move.from_uci("g1f3")   # White develops knight: 2. Nf3
    ],
    "rnbqkbnr/pppp-ppp/8/8/8/8/PPP-PPPP/RNBQKBNR w KQkq - 0 1": [
        chess.Move.from_uci("e2e4"),  # French Defense: 1. e4 e6
        chess.Move.from_uci("e7e6"),  # Black's response: 1... e6
        chess.Move.from_uci("d2d4")   # White develops pawn: 2. d4
    ],
    "rnbqkbnr/ppp-pppp/8/8/8/8/PPP-PPPP/RNBQKBNR w KQkq - 0 1": [
        chess.Move.from_uci("e2e4"),  # Caro-Kann Defense: 1. e4 c6
        chess.Move.from_uci("c7c6"),  # Black's response: 1... c6
        chess.Move.from_uci("d2d4")   # White develops pawn: 2. d4
    ],
    "rnbqkbnr/pppp-ppp/8/8/8/8/PPP-PPPP/RNBQKBNR w KQkq - 0 1": [
        chess.Move.from_uci("e2e4"),  # King's Gambit: 1. e4 e5
        chess.Move.from_uci("f2f4"),  # White sacrifices pawn: 2. f4
        chess.Move.from_uci("e7e5")   # Black's response: 2... e5
    ],
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": [
        chess.Move.from_uci("c2c4"),  # English Opening: 1. c4
        chess.Move.from_uci("e7e5"),  # Black's response: 1... e5
        chess.Move.from_uci("g1f3")   # White develops knight: 2. Nf3
    ],
    "rnbqkbnr/pppp-ppp/8/8/8/8/PPP-PPPP/RNBQKBNR w KQkq - 0 1": [
        chess.Move.from_uci("e2e4"),  # Scotch Game: 1. e4 e5
        chess.Move.from_uci("e7e5"),  # Black's response: 1... e5
        chess.Move.from_uci("d2d4")   # White develops pawn: 2. d4
    ],
    "rnbqkbnr/pppppppp/8/8/8/8/PPP-PPPP/RNBQKBNR w KQkq - 0 1": [
        chess.Move.from_uci("e2e4"),  # Ruy Lopez (Spanish Game): 1. e4 e5
        chess.Move.from_uci("e7e5"),  # Black's response: 1... e5
        chess.Move.from_uci("g1f3"),  # White develops knight: 2. Nf3
        chess.Move.from_uci("b1c3"),  # White develops knight: 3. Nc3
        chess.Move.from_uci("b8c6")   # Black develops knight: 3... Nc6
    ],
}