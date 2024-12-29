import random
import time
import chess
import pygame
from data import *

def square_is_on_board(square):
    # Check if the square index is within the valid range (0 to 63)
    return 0 <= square <= 63


def count_material(board: chess.Board, color: chess.Color) -> int:
    material = 0
    for piece_type in PIECE_VALUES:
        material += len(board.pieces(piece_type, color)) * PIECE_VALUES[piece_type]
    return material

class Player:
    def __init__(self, color, name):
        self.name = name
        self.color = color

    def get_move(self, board):
        pass

    def clear(self):
        pass

class HumanPlayer(Player):
    def __init__(self, color, name):
        super().__init__(color, name)
        self.selected_square = None
        self.move_made = None

    def get_move(self, board):
        move = self.move_made
        self.move_made = None
        return move

    def handle_events(self, events, board, board_obj):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                mouse_pos = pygame.mouse.get_pos()
                clicked_square = self.get_square_from_mouse_pos(mouse_pos, board)
                
                if clicked_square is not None:
                    piece = board_obj.piece_at(clicked_square)
                    
                    if self.selected_square is None and piece and piece.color == self.color:
                        self.selected_square = clicked_square
                    
                    elif self.selected_square is not None:
                        move = chess.Move(self.selected_square, clicked_square)
                        if move in board_obj.legal_moves:
                            self.move_made = move
                            self.selected_square = None  
                        else:
                            self.selected_square = None  

    def get_square_from_mouse_pos(self, mouse_pos, board):
        x, y = mouse_pos
        for square in chess.SQUARES:
            square_pos = board.get_square_position(square)
            square_rect = pygame.Rect(
                square_pos[0], square_pos[1], board.square_size, board.square_size
            )
            if square_rect.collidepoint(x, y):
                return square
        return None
    
    def clear(self):
        pass

class AI(Player):
    def __init__(self, color, name):
        super().__init__(color, name)

    def get_move(self, board):
        pass

class DummyAI(AI):
    def __init__(self, color, name):
        super().__init__(color, name)

    def get_move(self, board):
        return random.choice(list(board.legal_moves))
    
class IntermediateAI(AI):
    def __init__(self, color, name):
        super().__init__(color, name)
        self.max_depth = 4

    def get_move(self, board):
        if board.is_game_over():
            return None

        random_depth = self.get_dynamic_depth(board)
        move_evaluations = []

        for move in board.legal_moves:
            board.push(move)
            eval = self.alpha_beta(board, random_depth - 1, float('-inf'), float('inf'), not board.turn)
            board.pop()
            move_evaluations.append((move, eval))

        move_evaluations.sort(key=lambda x: x[1], reverse=board.turn)

        best_moves = [move for move, eval in move_evaluations if eval == move_evaluations[0][1]]
        return random.choice(best_moves)

    def get_dynamic_depth(self, board):
        move_count = board.fullmove_number
        if move_count <= 5:  # Early game
            return 2
        elif move_count <= 15:  # Middle game
            return 3
        else:  # Late game
            return 4

    def alpha_beta(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        if maximizing_player:
            max_eval = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self.alpha_beta(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self.alpha_beta(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            return min_eval
        
    def evaluate_board(self, board: chess.Board) -> int:
        if board.is_checkmate():
            return 10000 if board.turn else -10000
        if board.is_stalemate():
            return 0
        if board.is_insufficient_material():
            return 0
        
        # Enhanced evaluation with piece activity and king safety
        white_material = count_material(board, chess.WHITE)
        black_material = count_material(board, chess.BLACK)

        # Basic material difference
        eval_score = white_material - black_material

        # Additional factors like piece activity and king safety
        eval_score += self.evaluate_piece_activity(board)

        return eval_score

    def evaluate_piece_activity(self, board):
        white_activity = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.WHITE)
        black_activity = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.BLACK)
        return white_activity - black_activity
    

from evaluate import NNUE, Eval, Position  # Assuming Eval is the class containing the evaluate method

class AdvancedAI(AI):
    def __init__(self, color, name):
        super().__init__(color, name)
        self.base_max_depth = 5  # Max search depth
        self.eval_cache = {}  # Cache for evaluated positions
        self.base_max_move_time_cal = 3
        self.opening_sequence = None
        self.transposition_table = {}  # Transposition table for faster lookups

    def get_opening_move(self, board):
        # If no opening sequence has been selected, pick a random one from the opening book
        if self.opening_sequence is None:
            opening_key = board.fen()  # Use the current board FEN
            if opening_key in OPENING_BOOK:
                self.opening_sequence = OPENING_BOOK[opening_key]
            else:
                # Fall back to random opening key
                opening_key = random.choice(list(OPENING_BOOK.keys()))
                self.opening_sequence = OPENING_BOOK[opening_key]

        # Check if we still have remaining moves in the opening sequence
        if len(board.move_stack) < len(self.opening_sequence):
            # Return the next move from the opening sequence
            return self.opening_sequence[len(board.move_stack)]
        return None  # Fallback to standard AI move generation

    def get_move(self, board):
        opening_move = self.get_opening_move(board)
        if opening_move:
            return opening_move  # Return a move from the opening book

        best_move = None
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')

        start_time = time.time()
        
        for depth in range(3, self.base_max_depth + 1):
            if time.time() - start_time > self.base_max_move_time_cal:
                break
            
            current_best_move = None
            for move in self.order_moves(board):
                if time.time() - start_time > self.base_max_move_time_cal:
                    break
                board.push(move)
                eval = self.alpha_beta(board, depth, float('-inf'), float('inf'), board.turn == chess.WHITE)
                board.pop()

                if board.turn == chess.WHITE and eval > best_value:
                    best_value = eval
                    current_best_move = move
                elif board.turn == chess.BLACK and eval < best_value:
                    best_value = eval
                    current_best_move = move

            if current_best_move:
                best_move = current_best_move

        return best_move


    def alpha_beta(self, board, depth, alpha, beta, maximizing_player):
        board_fen = board.fen()  # Using FEN as cache key
        if board_fen in self.transposition_table:
            return self.transposition_table[board_fen]  # Return cached evaluation
        
        if board_fen in self.eval_cache:
            return self.eval_cache[board_fen]  # Return cached evaluation

        if depth == 0 or board.is_game_over():
            evaluation = self.evaluate_board(board)
            self.eval_cache[board_fen] = evaluation  # Cache evaluation
            self.transposition_table[board_fen] = evaluation  # Cache in transposition table
            return evaluation

        legal_moves = list(board.legal_moves)
        if maximizing_player:
            max_eval = float('-inf')
            for move in legal_moves:
                board.push(move)
                eval = self.alpha_beta(board, depth-1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            self.transposition_table[board_fen] = max_eval  # Cache result
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                eval = self.alpha_beta(board, depth-1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            self.transposition_table[board_fen] = min_eval  # Cache result
            return min_eval

    def order_moves(self, board):
        legal_moves = list(board.legal_moves)
        return sorted(
            legal_moves,
            key=lambda move: self.move_priority(board, move),
            reverse=True
        )

    def move_priority(self, board, move):
        board.push(move)
        evaluation = self.evaluate_board(board)
        board.pop()
        return evaluation
    
    def evaluate_board(self, board):
        position = self.convert_board_to_position(board)

        caches = {"small": {}, "big": {}}  # Placeholder caches
        optimism = 0

        # Pass the NNUE class directly
        evaluation = Eval.evaluate(NNUE, position, caches, optimism)

        return evaluation

    def convert_board_to_position(self, board):
        board_state = self.get_board_state(board)
        side_to_move = "WHITE" if board.turn else "BLACK"
        rule50_count = board.halfmove_clock
        key = board.fen()
        return Position(board_state, side_to_move, rule50_count, key)

    def get_board_state(self, board):
        board_state = []
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                board_state.append(piece.piece_type if piece.color else -piece.piece_type)
            else:
                board_state.append(0)  # Empty square
        return board_state

    
class Stockfish(AI):
    def __init__(self, color, name):
        super().__init__(color, name)
        self.engine_path = "engine/stockfish.exe"
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.engine.configure({"Threads": 2})
        self.analysis_time = 0.1

    def get_move(self, board):
        if board.is_game_over():
            return None
        
        result = self.engine.play(board, chess.engine.Limit(time=self.analysis_time))
        return result.move
    
    def clear(self):
        if hasattr(self, 'engine') and self.engine is not None:
            try:
                self.engine.quit()
            except Exception as e:
                print(f"Error during engine quit: {e}")
            finally:
                self.engine = None

    def __del__(self):
        try:
            self.clear()
        except Exception as e:
            print(f"Error during __del__: {e}")
