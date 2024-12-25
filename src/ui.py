import pygame

BACKGROUND_COLOR = (36, 44, 57)
WHITE_COL = (255, 255, 255)

class Menu:
    def __init__(self, screen, title, width, height, game):
        self.screen = screen
        self.game = game
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont('Arial', 36)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        
        self.play_button_rect = pygame.Rect(width // 2 - 100, height // 2 - 50, 200, 50)
        self.exit_button_rect = pygame.Rect(width // 2 - 100, height // 2 + 20, 200, 50)
        
        self.play_text = self.font.render("Play", True, (255, 255, 255))
        self.exit_text = self.font.render("Exit", True, (255, 255, 255))

        self.title_text = self.title_font.render(title, True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(width // 2, height // 4))
        
        self.in_menu = True

    def render(self):
        if self.in_menu:
            self.screen.fill(BACKGROUND_COLOR)
            
            self.screen.blit(self.title_text, self.title_rect)

            pygame.draw.rect(self.screen, (0, 150, 0), self.play_button_rect)
            pygame.draw.rect(self.screen, (150, 0, 0), self.exit_button_rect)
            
            self.screen.blit(self.play_text, self.play_text.get_rect(center=self.play_button_rect.center))
            self.screen.blit(self.exit_text, self.exit_text.get_rect(center=self.exit_button_rect.center))
        
        pygame.display.flip()

    def handle_events(self, events):
        """Handles menu-related events."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.play_button_rect.collidepoint(mouse_pos):
                    self.game.match_init()
                    self.in_menu = False  # Exit menu
                elif self.exit_button_rect.collidepoint(mouse_pos):
                    self.game.quit()

    def is_in_menu(self):
        return self.in_menu

class InGameUI:
    def __init__(self, screen, players, game):
        self.screen = screen
        self.players = players  # List of player objects or AI objects
        font_size = 25
        self.font = pygame.font.SysFont('Arial', font_size)
        self.game = game

        self.player1_text = self.font.render(f'{self.players[0].name}:', True, WHITE_COL)
        self.player2_text = self.font.render(f'{self.players[1].name}:', True, WHITE_COL)
        self.text_offset = game.BOARD_OFFSET[0] - self.player1_text.get_width()
        self.player1_pos = (self.text_offset, 0)
        self.player2_pos = (self.text_offset, game.HEIGHT - font_size)
        
        # UI Positions

        # Setup initial state

        # self.score_text = self.font.render(f"Score: {self.players[0].score} - {self.players[1].score}", True, (255, 255, 255))
        
    def render(self):

        self.screen.blit(self.player1_text, self.player1_pos)
        self.screen.blit(self.player2_text, self.player2_pos)

        if self.game.board.is_game_over():
            self.handle_game_over()

    def handle_game_over(self):
        if not self.game.board.is_game_over():
            return
        message = self.game.board.get_result()

        text = self.font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.screen.blit(text, text_rect)

        pygame.display.flip()

    def update_turn(self, turn):
        """Update the turn text based on the current player's turn."""
        self.turn_text = self.font.render(f"{self.players[turn].name}'s Turn", True, (255, 255, 255))

    def update_score(self, player_1_score, player_2_score):
        """Update the score display."""
        # self.score_text = self.font.render(f"Score: {player_1_score} - {player_2_score}", True, (255, 255, 255))
