import pygame
import time
import random
from data import *
from board import *
from pygame.locals import *
from player import *
from ui import *

TITLE = 'Chét ây ai'
class Game:
    def __init__(self):
        #window config
        self.BOARD_OFFSET = (200, 0)
        self.BOARD_WIDTH = 612
        self.BOARD_HEIGHT = 612
        self.WIDTH = self.BOARD_WIDTH + self.BOARD_OFFSET[0]
        self.HEIGHT = self.BOARD_HEIGHT + self.BOARD_OFFSET[1]
        
        #pygame initialize
        pygame.init()
        self.screen = pygame.display.set_mode([self.WIDTH, self.BOARD_HEIGHT]);
        pygame.display.set_caption(TITLE)
        self.font = pygame.font.SysFont('Arial', 48)

        #ui
        self.menu = Menu(self.screen, TITLE, self.WIDTH, self.HEIGHT, self)
        self.players = [None, None]
        self.running = True

        #time
        fps = 60
        self.target_update_time = 1/fps
        self.render_rate = 60
        self.render_clock = pygame.time.Clock()
        self.last_update_time = time.time()

    def match_init(self):
        #board initialize
        resource = GameResource()
        self.board = Board(self.BOARD_WIDTH, chess.WHITE, resource, self.BOARD_OFFSET)

        #PLAYER SETTING
        self.turn = 0
        
        self.players = [AdvancedAI(chess.WHITE, 'AdvanceAI1'), AdvancedAI(chess.BLACK, 'AdvanceAI2')]
        self.in_game_ui = InGameUI(self.screen, self.players, self)

        #run
        self.running = True

        #visualize
        self.animation_start_time = 0
        self.animation_duration = 0.3
        self.move_delay = 0.5

        self.is_animating = False
        self.start_pos = None
        self.end_pos = None
        self.piece_image = None
        self.last_move_time = time.time()
        self.on_move_square = None

    def run(self):
        while self.running:
            self.handle_input()
            
            current_time = time.time()
            elapsed_time = current_time - self.last_update_time

            if elapsed_time >= self.target_update_time:
                self.update(elapsed_time)
                self.last_update_time = current_time

            self.render()
            self.render_clock.tick(self.render_rate)
        pygame.quit()

    def update(self, delta_time):
        if self.menu.is_in_menu():
            return
        
        if self.board.is_game_over() or not self.running:
            self.quit()
            return
        if self.is_animating:
            return
        
        self.handle_players_turn()

    def render(self):
        if self.menu.is_in_menu():
            self.menu.render()
            return

        self.screen.fill(BACKGROUND_COLOR)
        self.board.render(self.screen, self.on_move_square)
        self.in_game_ui.render()

        if self.is_animating:
            self.render_animation()

        pygame.display.flip()

    #handle input
    def handle_input(self):
        events = pygame.event.get()
        for event in events:
            key_pressed = pygame.key.get_pressed()
            if event.type == QUIT :
                self.quit()
            elif key_pressed[K_ESCAPE]:
                self.return_menu()
            elif key_pressed[K_r]:
                self.reset()
        if self.menu.is_in_menu:
            self.menu.handle_events(events)

    def return_menu(self):
        for player in self.players:
            player.clear()
        self.menu.in_menu = True

    def quit(self):
        self.running = False  # Stop the game loop
        for player in self.players:
            player.clear()
    
    def reset(self):
        #TODO reset match
        pass

    def handle_players_turn(self):
        current_time = time.time()
        if current_time - self.last_move_time >= self.move_delay:
            move = self.players[self.turn].get_move(self.board.board)
            self.start_animation(move)
            self.board.move(move)
            self.last_move_time = current_time
            self.change_turn()

    def render_animation(self):
        elapsed_time = time.time() - self.animation_start_time
        t = min(elapsed_time / self.animation_duration, 1.0)
        current_x = self.start_pos[0] + t * (self.end_pos[0] - self.start_pos[0])
        current_y = self.start_pos[1] + t * (self.end_pos[1] - self.start_pos[1])

        self.board.render(self.screen, self.on_move_square)
        self.screen.blit(self.piece_image, (current_x, current_y))

        if t >= 1.0:
            self.is_animating = False
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
    
    def change_turn(self):
        self.turn = (self.turn + 1) % len(self.players)