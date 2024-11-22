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