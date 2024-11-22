import pygame
import chess

class Board:
    def __init__(self, size, resource, fen=chess.STARTING_FEN):
        self.size = size
        self.rows = self.cols = 8 
        self.square_size = self.size // self.rows
        self.fen = fen
        self.board = chess.Board(self.fen) 

        self.colors = [(240, 217, 181), (181, 136, 99)]
        self.piece_images = resource.load_piece_images(self.square_size)
        self.current_move = None

    def reset(self):
        self.board = chess.Board(chess.STARTING_BOARD_FEN)
    
    def move(self, move):
        if move in self.board.legal_moves:
            self.current_move = move

    def update_board_state_after_animation(self):
        self.board.push(self.current_move)

    def is_game_over(self):
        return self.board.is_game_over()
    
    def is_checkmate(self):
        return self.board.is_checkmate()
    
    def is_stalemate(self):
        return self.board.is_stalemate()
    
    def is_insufficient_material(self):
        return self.board.is_insufficient_material()
    
    def get_square_position(self, square):
        row = 7 - (square // 8)
        col = square % 8
        x = col * self.square_size
        y = row * self.square_size
        return (x, y)
    
    def get_piece_image_at_square(self, square):
        piece = self.board.piece_at(square)
        if piece:
            return self.piece_images[piece.symbol()]
        return None

    def render(self, screen, movesquare):
        # render the chessboard squares
        for row in range(self.rows):
            for col in range(self.cols):
                color = self.colors[(row + col) % 2]
                rect = pygame.Rect(
                    col * self.square_size, row * self.square_size, self.square_size, self.square_size
                )
                pygame.draw.rect(screen, color, rect)

        # render piecies
        for square in chess.SQUARES:
            if movesquare != square:
                piece = self.board.piece_at(square)
                if piece:
                    row = 7 - (square // 8)
                    col = square % 8
                    
                    piece_image = self.piece_images[piece.symbol()]
                    
                    screen.blit(piece_image, (col * self.square_size, row * self.square_size))
