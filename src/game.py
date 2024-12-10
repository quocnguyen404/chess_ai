import pygame
import time
import random
from data import *
from board import *
from pygame.locals import *
from player import *


class Game:
    font = None
    def __init__(self):

        #window config
        self.WIDTH_OFFSET = 300
        self.BOARD_OFFSET = (100, 0)
        self.WIDTH = self.HEIGHT = 612
        self.TURN_TEXT_OFFSET = self.BOARD_OFFSET[0] + self.WIDTH + 50

        #pygame initialize
        pygame.init()
        self.screen = pygame.display.set_mode([self.WIDTH + self.WIDTH_OFFSET, self.HEIGHT]);
        pygame.display.set_caption("Chét ây ai")
        Game.font = pygame.font.SysFont('Arial', 48)

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
        self.board = Board(self.WIDTH, chess.WHITE, resource, self.BOARD_OFFSET)

        #PLAYER SETTING
        self.turn = 0
        self.players = [AdvancedAI(chess.WHITE, 'DummyAI1'), AdvancedAI(chess.BLACK, 'DummyAI2')]

        self.gen_turn_text()
        # self.gen_move_value()

        #AI visualize
        self.animation_start_time = 0
        self.animation_duration = 0.3
        self.move_delay = 0.5

        self.is_animating = False
        self.start_pos = None
        self.end_pos = None
        self.piece_image = None
        self.last_move_time = time.time()
        self.on_move_square = None



    # def match_init(self):

    #     pass

    def run(self):
        while self.running:
            #handle input
            for event in pygame.event.get():
                key_pressed = pygame.key.get_pressed()
                if event.type == QUIT or key_pressed[K_ESCAPE]:
                    self.running = False
                elif key_pressed[K_r]:
                    self.reset()

            current_time = time.time()
            elapsed_time = current_time - self.last_update_time

            if elapsed_time >= self.target_update_time:
                self.update(elapsed_time)
                self.last_update_time = current_time

            self.render()

            self.render_clock.tick(self.render_rate)
        pygame.quit()
        

    def update(self, delta_time):
        if self.board.is_game_over() or not self.running:
            for player in self.players:
                player.clear()
            return
        
        if self.is_animating:
            return
        
        current_time = time.time()

        if current_time - self.last_move_time >= self.move_delay:
            move = self.players[self.turn].get_move(self.board.board)
            self.start_animation(move)
            self.board.move(move)
            self.last_move_time = current_time
            self.change_turn()

    def render(self):
        self.screen.fill((37, 150, 190))
        self.board.render(self.screen, self.on_move_square)

        if self.is_animating:
            self.render_animation()

        # render turn text
        self.screen.blit(self.turn_text, (self.TURN_TEXT_OFFSET, 0))
        # self.screen.blit(self.value_text, (self.TURN_TEXT_OFFSET, 50))
        self.render_game_over()
        pygame.display.flip()

    def render_animation(self):
        #linear interpolate
        elapsed_time = time.time() - self.animation_start_time
        t = min(elapsed_time / self.animation_duration, 1.0)  #Normalize time to [0, 1]
        current_x = self.start_pos[0] + t * (self.end_pos[0] - self.start_pos[0])
        current_y = self.start_pos[1] + t * (self.end_pos[1] - self.start_pos[1])

        self.board.render(self.screen, self.on_move_square)
        self.screen.blit(self.piece_image, (current_x, current_y))

        if t >= 1.0:
            #end animating
            self.is_animating = False
            #apply move to board
            self.board.update_board_state_after_animation()

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
        message = self.board.get_result()

        text = self.font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(4000)
    
    def change_turn(self):
        if(self.turn == len(self.players) - 1):
           self.turn = 0
        else:
            self.turn += 1
        self.gen_turn_text()
        # self.gen_move_value()
        

    def gen_turn_text(self):
        str_turn = ''
        if(self.turn == 0):
            str_turn = 'White'
        else:
            str_turn = 'Black'
        self.turn_text = Game.font.render(str_turn, True, (0, 0, 0))
