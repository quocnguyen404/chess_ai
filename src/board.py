import pygame
import chess

class Board:
    def __init__(self, size, facing_color, resource, offset, fen=chess.STARTING_FEN):
        self.size = size
        self.rows = self.cols = 8 
        self.square_size = self.size // self.rows
        self.offset = offset

        self.board = chess.Board(fen)
        self.colors = [(240, 217, 181), (181, 136, 99)]
        self.piece_images = resource.load_piece_images(self.square_size)

        self.current_move = None
        self.facing_color = facing_color
        self.font = pygame.font.SysFont('Arial', 12)

    def move(self, move):
        if move in self.board.legal_moves:
            self.current_move = move

    def update_board_state_after_animation(self):
        self.board.push(self.current_move)

    def is_game_over(self):
        return self.board.is_game_over()
        
    def get_square_index(self, square):
        row = 7 - (square // 8) if self.facing_color != chess.BLACK else (square // 8)
        col = square % 8 if self.facing_color != chess.BLACK else 7 - (square % 8)
        return (row, col)
    
    def get_square_position(self, square):
        (row, col) = self.get_square_index(square)

        x = col * self.square_size + self.offset[0]
        y = row * self.square_size + self.offset[1]
        return (x, y)
    
    def get_piece_image_at_square(self, square):
        piece = self.board.piece_at(square)
        if piece:
            return self.piece_images[piece.symbol()]
        return None

    def render(self, screen, movesquare):
        for square in chess.SQUARES:
            self.render_square(screen, square)
            if movesquare != square:
                piece = self.board.piece_at(square)
                if piece:
                    piece_image = self.piece_images[piece.symbol()]
                    piece_position = self.get_square_position(square)
                    
                    screen.blit(piece_image, piece_position)

                    #Debug text piece infor
                    # text_surface = self.font.render(piece.symbol(), True, (0, 0, 0))
                    # screen.blit(text_surface, piece_position)

    def render_square(self, screen, square):
        (row, col) = self.get_square_index(square)
        color = self.colors[(row + col) % 2]

        rect = pygame.Rect(
            col * self.square_size + self.offset[0], row * self.square_size + self.offset[1], self.square_size, self.square_size
        )

        pygame.draw.rect(screen, color, rect)

        # Debug text square infor
        # text_surface = self.font.render(chess.square_name(square), True, (0, 0, 0))
        # text_surface_index = self.font.render(str(square), True, (0, 0, 0))

        # text_rect = text_surface.get_rect(bottomleft=rect.bottomleft)
        # text_rect_index = text_surface_index.get_rect(bottomright=rect.bottomright)
        # screen.blit(text_surface, text_rect)
        # screen.blit(text_surface_index, text_rect_index)