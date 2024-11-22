import pygame
import time
from data import *
from board import *
from pygame.locals import *
from ai import *


class Game:

    def __init__(self):
        #pygame initialize
        self.WIDTH = self.HEIGHT = 612

        pygame.init()
        self.screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT]);
        pygame.display.set_caption("Chét ây ai")

        #loop
        self.running = True

        #time
        fps = 60
        self.target_update_time = 1/fps
        self.render_rate = 60
        self.render_clock = pygame.time.Clock()
        self.last_update_time = time.time()

        #board initialize
        resource = GameResource()
        self.board = Board(self.WIDTH, resource)

        #ai
        self.ai1 = AI()
        self.ai2 = AI()

        #message
        self.font = pygame.font.SysFont(None, 48)

        #AI visualize
        self.current_turn = "AI1"
        self.is_animating = False
        self.animation_start_time = 0
        self.animation_duration = 0.1
        self.move_delay = 0.1
        self.start_pos = None
        self.end_pos = None
        self.piece_image = None
        self.last_move_time = time.time()
        self.on_move_square = None


    def run(self):
        while not self.board.is_game_over() and self.running:
            for event in pygame.event.get():
                key_pressed = pygame.key.get_pressed()
                if event.type == QUIT or key_pressed[K_ESCAPE]:
                    self.running = False
                elif key_pressed[K_r]:
                    self.board.reset()

            current_time = time.time()
            elapsed_time = current_time - self.last_update_time

            if elapsed_time >= self.target_update_time:
                self.update(elapsed_time)
                self.last_update_time = current_time

            self.render()

            self.render_clock.tick(self.render_rate)

        pygame.quit()

    def render(self):
        self.board.render(self.screen, self.on_move_square)

        if self.is_animating:
            self.render_animation()

        self.render_game_over()

        pygame.display.flip()

    def update(self, delta_time):
        if not self.is_animating:
            current_time = time.time()
            if current_time - self.last_move_time >= self.move_delay:
                if self.current_turn == "AI1":
                    move = self.ai1.get_move(self.board)
                    self.start_animation(move)  # Start animation for AI1
                    self.board.move(move)
                    self.current_turn = "AI2"
                elif self.current_turn == "AI2":
                    move = self.ai2.get_move(self.board)
                    self.start_animation(move)  # Start animation for AI2
                    self.board.move(move)
                    self.current_turn = "AI1"
                self.last_move_time = current_time

    def render_animation(self):
        elapsed_time = time.time() - self.animation_start_time
        t = min(elapsed_time / self.animation_duration, 1.0)  # Normalize time to [0, 1]
        current_x = self.start_pos[0] + t * (self.end_pos[0] - self.start_pos[0])
        current_y = self.start_pos[1] + t * (self.end_pos[1] - self.start_pos[1])

        self.board.render(self.screen, self.on_move_square)
        self.screen.blit(self.piece_image, (current_x, current_y))

        if t >= 1.0:
            self.is_animating = False  # End animation
            self.board.update_board_state_after_animation()  # Apply move to board

    def start_animation(self, move):

        self.is_animating = True
        self.animation_start_time = time.time()

        start_square = move.from_square
        end_square = move.to_square
        self.on_move_square = start_square

        self.start_pos = self.board.get_square_position(start_square)
        self.end_pos = self.board.get_square_position(end_square)

        self.piece_image = self.board.get_piece_image_at_square(start_square)
    
    def render_game_over(self):
        if not self.board.is_game_over():
            return
        
        if self.board.is_checkmate():
            message = "Checkmate!"
        elif self.board.is_stalemate():
            message = "Stalemate!"
        elif self.board.is_insufficient_material():
            message = "Draw: Insufficient Material!"
        
        text = self.font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(4000)
        