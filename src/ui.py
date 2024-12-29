import chess
import pygame

BACKGROUND_COLOR = (36, 44, 57)
WHITE_COL = (255, 255, 255)
BUTTON_COL1 = (0, 150, 0)
BUTTON_COL2 = (150, 0, 0)

class Menu:
    def __init__(self, screen, title, width, height, game):
        self.screen = screen
        self.game = game
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont('Arial', 36)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)

        center = (width // 2, height // 2)
        self.title_text = self.title_font.render(title, True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(center[0], center[1] - 220))

        case1_btn_rect = pygame.Rect(center[0] - 100, center[1] - 150, 200, 50)
        case2_btn_rect = pygame.Rect(center[0] - 100, center[1] - 80, 200, 50)
        case3_btn_rect = pygame.Rect(center[0] - 100, center[1] - 10, 200, 50)
        case4_btn_rect = pygame.Rect(center[0] - 100, center[1] + 60, 200, 50)
        case5_btn_rect = pygame.Rect(center[0] - 100, center[1] + 130, 200, 50)
        self.btns = [
            case1_btn_rect,
            case2_btn_rect,
            case3_btn_rect,
            case4_btn_rect,
            case5_btn_rect,
        ]
        self.exit_btn_rect = pygame.Rect(center[0] - 100, center[1] + 200, 200, 50)

        case1_text = self.font.render("Player vs AI", True, WHITE_COL)
        case2_text = self.font.render("Dum vs Inter", True, WHITE_COL)
        case3_text = self.font.render("Advan vs Advan", True, WHITE_COL)
        case4_text = self.font.render("Advan vs Inter", True, WHITE_COL)
        case5_text = self.font.render("Sf vs Sf", True, WHITE_COL)
        self.cases_texts = [
            case1_text,
            case2_text,
            case3_text,
            case4_text,
            case5_text,
        ]
        self.exit_text = self.font.render("Exit", True, WHITE_COL)
        self.in_menu = True

    def render(self):
        if self.in_menu:
            self.screen.fill(BACKGROUND_COLOR)
            self.screen.blit(self.title_text, self.title_rect)

            for i, btn in enumerate(self.btns):
                pygame.draw.rect(self.screen, BUTTON_COL1, btn)
                text_surface = self.cases_texts[i]
                text_rect = text_surface.get_rect(center=btn.center)
                self.screen.blit(text_surface, text_rect)
                
            pygame.draw.rect(self.screen, BUTTON_COL2, self.exit_btn_rect)
            exit_text_rect = self.exit_text.get_rect(center=self.exit_btn_rect.center)
            self.screen.blit(self.exit_text, exit_text_rect)
            
        pygame.display.flip()

    def handle_events(self, events):
        """Handles menu-related events."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.exit_btn_rect.collidepoint(mouse_pos):
                    self.game.quit()
                for i in range(len(self.btns)):
                    if self.btns[i].collidepoint(mouse_pos):
                        self.in_menu = False  # Exit menu
                        self.game.pick_case(i)
    

class PickLevelUI:
    def __init__(self, screen, width, height, game):
        self.screen = screen
        self.game = game
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont('Arial', 36)

        center = (width // 2, height // 2)
        case1_btn_rect = pygame.Rect(center[0] - 100, center[1] - 150, 200, 50)
        case2_btn_rect = pygame.Rect(center[0] - 100, center[1] - 80, 200, 50)
        case3_btn_rect = pygame.Rect(center[0] - 100, center[1] - 10, 200, 50)
        case4_btn_rect = pygame.Rect(center[0] - 100, center[1] + 60, 200, 50)
        self.btns = [
            case1_btn_rect,
            case2_btn_rect,
            case3_btn_rect,
            case4_btn_rect,
        ]
        self.exit_btn_rect = pygame.Rect(center[0] - 100, center[1] + 200, 200, 50)

        case1_text = self.font.render("Dummy AI", True, WHITE_COL)
        case2_text = self.font.render("Intermediate", True, WHITE_COL)
        case3_text = self.font.render("AdvancedAI", True, WHITE_COL)
        case4_text = self.font.render("Stockfish", True, WHITE_COL)
        self.cases_texts = [
            case1_text,
            case2_text,
            case3_text,
            case4_text,
        ]
        self.exit_text = self.font.render("Exit", True, WHITE_COL)
        self.in_pick = True

    def render(self):
        if self.in_pick:
            self.screen.fill(BACKGROUND_COLOR)

            for i, btn in enumerate(self.btns):
                pygame.draw.rect(self.screen, BUTTON_COL1, btn)
                text_surface = self.cases_texts[i]
                text_rect = text_surface.get_rect(center=btn.center)
                self.screen.blit(text_surface, text_rect)
                
            pygame.draw.rect(self.screen, BUTTON_COL2, self.exit_btn_rect)
            exit_text_rect = self.exit_text.get_rect(center=self.exit_btn_rect.center)
            self.screen.blit(self.exit_text, exit_text_rect)
            
        pygame.display.flip()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.exit_btn_rect.collidepoint(mouse_pos):
                    self.game.return_menu()
                    self.in_pick = False
                for i in range(len(self.btns)):
                    if self.btns[i].collidepoint(mouse_pos):
                        self.game.handle_pick_level(i)
                        self.in_pick = False

class InGameUI:
    def __init__(self, screen, players, game):
        self.screen = screen
        self.players = players 
        font_size = 25
        self.font = pygame.font.SysFont('Arial', font_size)
        self.eg_font = pygame.font.SysFont('Arial', 50)
        self.game = game
        self.player1_text = self.font.render(f'{self.players[0].name}:', True, WHITE_COL)
        self.player2_text = self.font.render(f'{self.players[1].name}:', True, WHITE_COL)
        self.text1_offset = game.BOARD_OFFSET[0] - self.player1_text.get_width()
        self.text2_offset = game.BOARD_OFFSET[0] - self.player2_text.get_width()
        if game.facing_color == chess.WHITE:
            self.player1_pos = (self.text1_offset, game.HEIGHT - font_size - 50)
            self.player2_pos = (self.text2_offset, 0)
        else:
            self.player2_pos = (self.text2_offset, game.HEIGHT - font_size - 50)
            self.player1_pos = (self.text1_offset, 0)

        btn_font = pygame.font.SysFont('Arial', 15)
        self.reset_text = btn_font.render('Reset', True, WHITE_COL)
        self.pause_text = btn_font.render('Pause', True, WHITE_COL)
        self.exit_text = btn_font.render('Exit', True, WHITE_COL)

        self.reset_btn = pygame.Rect(0, 0, 50, 50)
        self.pause_btn = pygame.Rect(0, 60, 50, 50)
        self.exit_btn = pygame.Rect(0,120, 50, 50)
        
    def render(self):
        self.screen.blit(self.player1_text, self.player1_pos)
        self.screen.blit(self.player2_text, self.player2_pos)

        pygame.draw.rect(self.screen, BUTTON_COL1, self.reset_btn)

        if self.game.pausing:
            pygame.draw.rect(self.screen, BUTTON_COL2, self.pause_btn)
        else:
            pygame.draw.rect(self.screen, BUTTON_COL1, self.pause_btn)

        pygame.draw.rect(self.screen, BUTTON_COL2, self.exit_btn)

        self.screen.blit(self.reset_text, self.reset_text.get_rect(center=self.reset_btn.center))
        self.screen.blit(self.pause_text, self.pause_text.get_rect(center=self.pause_btn.center))
        self.screen.blit(self.exit_text, self.exit_text.get_rect(center=self.exit_btn.center))
        self.screen.blit(self.turn_text, (0, self.game.HEIGHT // 2))
        if self.game.board.is_game_over():
            self.handle_game_over()

    def handle_game_over(self):
        if not self.game.board.is_game_over():
            return
        result = self.game.board.board.result()  # This will return '1-0', '0-1', or '1/2-1/2'
        if result == '1-0':
            message = f"{self.players[0].name} wins!"  # White wins
        elif result == '0-1':
            message = f"{self.players[1].name} wins!"  # Black wins
        elif result == '1/2-1/2':
            message = "It's a draw!"  # Draw condition

        text = self.eg_font.render(message, True, WHITE_COL)
        text_rect = text.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT // 2))
        self.screen.blit(text, text_rect)

        pygame.display.flip()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.reset_btn.collidepoint(mouse_pos):
                    self.game.reset()
                elif self.pause_btn.collidepoint(mouse_pos):
                    self.game.pause()
                elif self.exit_btn.collidepoint(mouse_pos):
                    self.game.return_menu()

    def update_turn(self, turn):
        self.turn_text = self.font.render(f"{self.players[turn].name}'s Turn", True, (255, 255, 255))
