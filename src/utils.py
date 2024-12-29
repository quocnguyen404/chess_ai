import os
import pygame
import chess.engine


def cut_spritesheet(sheet_path, sprites_per_row, sprites_per_column):
    sprite_sheet = pygame.image.load(sheet_path)
    sheet_width, sheet_height = sprite_sheet.get_size()

    sprite_width = sheet_width // sprites_per_row
    sprite_height = sheet_height // sprites_per_column

    sprite_images = []
    
    # Loop to crop each sprite from the sheet
    for row in range(sprites_per_column):
        for col in range(sprites_per_row):
            left = col * sprite_width
            top = row * sprite_height
            right = left + sprite_width
            bottom = top + sprite_height

            sprite = sprite_sheet.subsurface(pygame.Rect(left, top, sprite_width, sprite_height))
            sprite_images.append(sprite)
    
    return sprite_images

