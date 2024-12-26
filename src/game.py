import sys
import pygame
import time
import random
from data import *
from board import *
from pygame.locals import *
from player import *
from ui import *

TITLE = 'Chess'
class Game:
    cases = None
    def __init__(self):
        #window config
        self.BOARD_OFFSET = (300, 0)
        self.BOARD_WIDTH = 612
        self.BOARD_HEIGHT = 612
        self.WIDTH = self.BOARD_WIDTH + self.BOARD_OFFSET[0]
        self.HEIGHT = self.BOARD_HEIGHT + self.BOARD_OFFSET[1]
        
        #pygame initialize
        pygame.init()
        self.screen = pygame.display.set_mode([self.WIDTH, self.BOARD_HEIGHT]);
        pygame.display.set_caption(TITLE)
        self.font = pygame.font.SysFont('Arial', 48)

        Game.cases = [
            [HumanPlayer(chess.WHITE, 'Player'), DummyAI(chess.BLACK, 'Dummy AI2')],
            [DummyAI(chess.WHITE, 'Dummy AI'), IntermediateAI(chess.BLACK, 'Intermediate AI')],
            [IntermediateAI(chess.WHITE, 'Intermediate AI1'), IntermediateAI(chess.BLACK, 'Intermediate AI2')],
            [AdvancedAI(chess.WHITE, 'Stockfish'), IntermediateAI(chess.BLACK, 'Group5')],
            [AdvancedAI(chess.WHITE, 'Magnus Carlsen'), AdvancedAI(chess.BLACK, 'Hikaru Nakamura')],
        ]

        #ui
        self.menu = Menu(self.screen, TITLE, self.WIDTH, self.HEIGHT, self)
        self.players = [None, None]

        #flag
        self.running = True
        self.pausing = False
        self.facing_color = chess.WHITE

        #time
        fps = 60
        self.target_update_time = 1/fps
        self.render_rate = 60
        self.render_clock = pygame.time.Clock()
        self.last_update_time = time.time()

    def match_init(self):
        #board initialize
        resource = GameResource()
        self.board = Board(self.BOARD_WIDTH, self.facing_color, resource, self.BOARD_OFFSET)


        self.turn = 0
        self.in_game_ui = InGameUI(self.screen, self.players, self)
        self.in_game_ui.update_turn(self.turn)

        #visualize
        self.animation_start_time = 0
        self.animation_duration = 0.5
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
        self.clear()

    def update(self, delta_time):
        if self.menu.is_in_menu() or self.pausing:
            return
        if not self.running or self.board.is_game_over():
            return
        if self.is_animating:
            return
        
        self.handle_players_turn()

    def render(self):
        if self.menu.is_in_menu():
            self.menu.render()
            return

        self.screen.fill(BACKGROUND_COLOR)
        
        selected_square = None
        if isinstance(self.players[self.turn], HumanPlayer):
            selected_square = self.players[self.turn].selected_square

        self.board.render(self.screen, self.on_move_square, selected_square=selected_square)
        self.in_game_ui.render()

        if self.is_animating:
            self.render_animation()

        pygame.display.flip()

    #handle input
    def handle_input(self):
        events = pygame.event.get()
        for event in events:
            key_pressed = pygame.key.get_pressed()
            if event.type == QUIT:
                self.quit()
            elif key_pressed[K_ESCAPE]:
                self.return_menu()

        if self.menu.in_menu:
            self.menu.handle_events(events)
        else:
            self.in_game_ui.handle_events(events)
            if isinstance(self.players[self.turn], HumanPlayer):
                self.players[self.turn].handle_events(events, self.board, self.board.board)


    def return_menu(self):
        self.menu.in_menu = True

    def quit(self):
        self.running = False  # Stop the game loop
        for player in self.players:
            if player:
                player.clear()

    def pause(self):
        self.pausing = not self.pausing
    
    def reset(self):
        self.match_init()

    def pick_case(self, case_index):
        selected_case = Game.cases[case_index][:]
        random.shuffle(selected_case)
        white_player, black_player = selected_case
        white_player.color, black_player.color = chess.WHITE, chess.BLACK
        self.players = [white_player, black_player]
        if isinstance(black_player, HumanPlayer):
            self.facing_color = chess.BLACK
        self.match_init()
            
        
    def handle_players_turn(self):
        current_player = self.players[self.turn]
        
        if isinstance(current_player, HumanPlayer):
            move = current_player.get_move(self.board.board)
            if move:
                self.board.move(move)
                self.start_animation(move)
                self.change_turn()
        else:
            current_time = time.time()
            if current_time - self.last_move_time >= self.move_delay:
                move = current_player.get_move(self.board.board)
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
            self.board.update_board_state_after_animation()
            self.is_animating = False

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
        self.in_game_ui.update_turn(self.turn)

    def clear(self):
        for kaces in Game.cases:
            kaces[0].clear()
            kaces[1].clear()

    def __del__(self):
        self.clear()