import random
import time
import chess
import pygame
from data import opening_book

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 100,  
}

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
        eval_score += self.evaluate_king_safety(board)

        return eval_score

    def evaluate_piece_activity(self, board):
        white_activity = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.WHITE)
        black_activity = sum(1 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.BLACK)
        return white_activity - black_activity

    def evaluate_king_safety(self, board):
        # Simple king safety heuristic: distance to the center
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)
        white_king_safety = abs(chess.square_rank(white_king) - 3) + abs(chess.square_file(white_king) - 3)
        black_king_safety = abs(chess.square_rank(black_king) - 3) + abs(chess.square_file(black_king) - 3)
        return black_king_safety - white_king_safety

CENTER_8_SQUARES = {
    chess.C4, chess.C5,
    chess.D4, chess.D5,
    chess.E4, chess.E5,
    chess.F4, chess.F5
}

class AdvancedAI(AI):
    def __init__(self, color, name):
        super().__init__(color, name)
        self.base_max_depth = 5  # Max search depth
        self.eval_cache = {}  # Cache for evaluated positions
        self.base_max_move_time_cal = 4

    def get_move(self, board: chess.Board):
        move_count = board.fullmove_number
        remaining_pieces = sum(1 for sq in chess.SQUARES if board.piece_at(sq))
        self.max_depth = self.base_max_depth + self.adjust_depth(move_count, remaining_pieces)
        self.max_move_time_cal = self.base_max_move_time_cal + self.adjust_time(move_count, remaining_pieces)

        best_move = None
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
        start_time = time.time()
        for depth in range(1, self.max_depth + 1):
            if time.time() - start_time > self.max_move_time_cal:  # Time limit for move calculation
                break

            current_best_move = None
            for move in self.order_moves(board):
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

    def adjust_depth(self, move_count, remaining_pieces):
        # Early game (move count <= 20) with many pieces
        if move_count <= 20 and remaining_pieces > 20:  
            return 2  # Medium depth for better planning
        # Midgame (move count 20-40) with some pieces left
        elif 20 < move_count <= 40 and remaining_pieces > 10:  
            return 3  # Deeper depth for more complex analysis
        # Endgame (move count > 40) with few pieces left
        elif remaining_pieces <= 10:  
            return 4  # Shallow depth but focus on precise tactics
        # Default case (late game, fewer pieces)
        return 1

    def adjust_time(self, move_count, remaining_pieces):
        # Early game, many pieces
        if move_count <= 20 and remaining_pieces > 20:  
            return 1  # Faster time allocation for opening moves
        # Midgame, fewer pieces
        elif 20 < move_count <= 40 and remaining_pieces > 10:  
            return 2  # Slightly longer to think about exchanges
        # Late game, few pieces left
        elif remaining_pieces <= 10:  
            return 3  # More time for precise endgame tactics
        # Default time allocation
        return 1

    def order_moves(self, board):
        legal_moves = list(board.legal_moves)  # Ensure these are all legal moves
        return sorted(
            legal_moves,
            key=lambda move: self.move_priority(board, move),
            reverse=True
        )
        
    def alpha_beta(self, board, depth, alpha, beta, maximizing_player):
        board_hash = hash(board.fen())  # Use the board's FEN string for unique identification
        if board_hash in self.eval_cache:
            return self.eval_cache[board_hash]  # Return cached evaluation if available

        if depth == 0 or board.is_game_over():
            evaluation = self.evaluate_board(board)
            self.eval_cache[board_hash] = evaluation  # Cache the result
            return evaluation

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
            self.eval_cache[board_hash] = max_eval  # Cache the result
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
            self.eval_cache[board_hash] = min_eval  # Cache the result
            return min_eval

    def evaluate_board(self, board):
        # 1. Material Balance
        material_value = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                piece_type = piece.piece_type  # Get the piece type (e.g., PAWN, KNIGHT)
                piece_color = piece.color  # True for white, False for black
                piece_val = PIECE_VALUES[piece_type]
                # Adjust for the piece's position using the piece-square table
                material_value += piece_val * self.piece_square_table(piece_type, square, piece_color)
        # 2. Pawn Structure Evaluation
        material_value += self.pawn_structure_evaluation(board)
        # 3. King Safety Evaluation
        material_value += self.king_safety_evaluation(board)
        # 4. Piece Activity Evaluation (development, mobility)
        material_value += self.evaluate_piece_activity(board)
        # 5. Center Control Evaluation
        material_value += self.evaluate_center_control(board)
        # 6. Passed Pawn Evaluation
        material_value += self.evaluate_passed_pawns(board)
        # 7. Piece Coordination (Good development and coordination of pieces)
        material_value += self.evaluate_piece_coordination(board)

        return material_value
    
    def move_priority(self, board, move):
        """Assign priority to a move based on various heuristics, including the opening book."""
        priority = 0

        # Check if the current position is in the opening book
        if board.fen() in opening_book:
            opening_moves = opening_book[board.fen()]
            # If the move is part of the opening book, prioritize it
            if move in opening_moves:
                priority += 30  # Give high priority to opening book moves

        # Simulate the move on a temporary board
        temp_board = board.copy()  # Copy the board to simulate the move
        temp_board.push(move)  # Make the move on the temporary board

        # Check if the move leaves the current player's king in check
        if temp_board.is_check():  # If the king is in check, this is not a valid move
            temp_board.pop()  # Undo the move
            return -1  # Invalid move, assign the lowest priority

        # Now check if the move gives check to the opponent's king
        opponent_in_check = temp_board.is_check()

        if temp_board.is_checkmate() and temp_board.turn == board.turn:
            return -1  # Avoid checkmate moves

        # Initialize the priority
        if opponent_in_check:
            priority += 20  # Prioritize check moves (higher than normal moves)

        # Check if the move results in checkmate
        if temp_board.is_checkmate():
            priority += 50  # Checkmate should have the highest priority

        # Check if the move is a capture
        is_capture = temp_board.is_capture(move)
        if is_capture:
            priority += 10  # Captures are prioritized

            # Evaluate the value of the captured piece
            captured_piece = temp_board.piece_at(move.to_square)
            captured_piece_value = PIECE_VALUES.get(captured_piece.piece_type, 0) if captured_piece else 0
            priority += captured_piece_value  # Increase priority based on captured piece value

        # Control of the center (d4, d5, e4, e5)
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        if move.to_square in center_squares:
            priority += 5  # Central squares are more valuable

        # Evaluate piece activity (mobility)
        piece_mobility = len(list(temp_board.legal_moves))  # Mobility of the current piece
        priority += piece_mobility  # The more moves a piece has, the higher its priority

        # King safety evaluation (moves that improve king safety are prioritized)
        if temp_board.king(temp_board.turn) == move.from_square:
            # If it's a king move, prioritize moves that keep the king safe (e.g., castling)
            king_square = move.to_square
            attacks = len(temp_board.attacks(king_square))
            priority -= attacks * 5  # Penalize moves that expose the king to attacks

        # Evaluate pawn structure (prevent creating weaknesses, advancing passed pawns)
        if temp_board.piece_at(move.to_square) and temp_board.piece_at(move.to_square).piece_type == chess.PAWN:
            if self.is_passed(temp_board, move.to_square, temp_board.turn):
                priority += 15  # Passed pawn advancing is highly valuable
            elif self.is_isolated(temp_board, move.to_square):
                priority -= 10  # Isolated pawns are a weakness
            elif self.is_backward(temp_board, move.to_square):
                priority -= 5  # Backward pawns are a weakness

        # Evaluate piece coordination (support between pieces)
        if self.is_piece_coordination_good(temp_board, move):
            priority += 5  # Favor moves that improve piece coordination

        # Evaluate tactical threats (e.g., forks, pins, skewers)
        if self.is_tactical_threat(temp_board, move):
            priority += 10  # Prioritize moves that create tactical opportunities

        # If the move is a pawn promotion (special case), give it high priority
        if move.promotion:
            priority += 25  # Pawn promotion should be highly prioritized (e.g., promote to queen)

        # Penalize moves that leave a piece in danger (under attack)
        if self.is_under_attack(temp_board, move.to_square, temp_board.turn):
            priority -= 15  # Penalize moves that leave a piece in danger

        # Add more prioritization for piece development (e.g., Nf3, Nc3)
        if move.from_square == chess.E2 and move.to_square == chess.E4:
            priority += 10  # Prioritize central control (e.g., pawn to e4)
        elif move.from_square == chess.G1 and move.to_square == chess.F3:
            priority += 15  # Prioritize knight development (e.g., Nf3)
        elif move.from_square == chess.B1 and move.to_square == chess.C3:
            priority += 15  # Prioritize knight development (e.g., Nc3)
        # Avoid unnecessary king moves early
        if move.from_square == chess.E1 and move.to_square != chess.G1:  # King move, but not castling
            priority -= 10  # Penalize king moves unless castling

        temp_board.pop()  # Undo the move
        return priority
    
    def is_under_attack(self, board, square, color):
        opponent_color = chess.WHITE if color == chess.BLACK else chess.BLACK
        # Check all attacks from opponent's pieces to the given square
        return any(board.piece_at(target_square) and board.piece_at(target_square).color == opponent_color
                for target_square in board.attacks(square))

    def is_castling_legal(self, board, move):
        """Check if castling is legal based on various conditions (king, rook movement, no checks)."""
        # Ensure the king and rook haven't moved, squares between them are empty, and the king isn't in check
        if not board.is_castling(move):
            return False
        if board.is_check():
            return False
        if board.is_king_in_check(board.turn):
            return False
        return True

    def is_en_passant_legal(self, board, move):
        """Check if en passant is legal based on the current state of the game."""
        # En passant is only valid under very specific circumstances (e.g., opponent just moved a pawn two squares)
        # You need to check if the move matches the en passant condition:
        if board.piece_at(move.from_square).piece_type == chess.PAWN and board.piece_at(move.to_square) is None:
            if move.from_square == chess.E5 and move.to_square == chess.D6:
                return True  # Example condition for en passant
        return False

    def is_piece_coordination_good(self, board, move):
        piece = board.piece_at(move.from_square)
        
        if piece is None:
            return False  
        
        piece_type = piece.piece_type

        # Simple check for rooks and queens, prefer moves that place them on open files or ranks
        if piece_type == chess.ROOK or piece_type == chess.QUEEN:
            for target_square in chess.SQUARES:
                target_piece = board.piece_at(target_square)
                if target_piece and (target_piece.piece_type == chess.ROOK or target_piece.piece_type == chess.QUEEN):
                    if chess.square_file(move.from_square) == chess.square_file(target_square) or \
                    chess.square_rank(move.from_square) == chess.square_rank(target_square):
                        return True  # Pieces on the same file/rank are more coordinated

        return False

    def is_tactical_threat(self, board, move):
        """Check if a move creates any tactical threats such as forks, pins, or skewers"""
        # Implementing tactical threat detection (this can be made more complex)
        attacked_piece = board.piece_at(move.to_square)
        if attacked_piece:
            if attacked_piece.color != board.turn:  # If it attacks an opponent's piece
                if self.is_fork(board, move):
                    return True
                elif self.is_pin(board, move):
                    return True
                elif self.is_skewer(board, move):
                    return True
        return False

    def is_fork(self, board, move):
        """Check if the move sets up a fork (attacking two pieces at once)"""
        # This is a simplified version; real fork detection requires checking multiple pieces
        attacked_piece = board.piece_at(move.to_square)
        if attacked_piece:
            for target_square in chess.SQUARES:
                target_piece = board.piece_at(target_square)
                if target_piece and target_piece.color != board.turn:
                    if len(board.attackers(board.turn, target_square)) > 1:  # Attacking both pieces
                        return True
        return False

    def is_pin(self, board, move):
        """Check if the move sets up a pin"""
        # A pin occurs when a piece is attacked and cannot move without exposing a more valuable piece
        attacked_piece = board.piece_at(move.to_square)
        if attacked_piece:
            for target_square in chess.SQUARES:
                target_piece = board.piece_at(target_square)
                if target_piece and target_piece.color != board.turn:
                    if len(board.attackers(board.turn, target_square)) > 1:  # More attackers means a pin is possible
                        return True
        return False

    def is_skewer(self, board, move):
        """Check if the move sets up a skewer"""
        # A skewer is similar to a pin, but with the more valuable piece in front
        attacked_piece = board.piece_at(move.to_square)
        if attacked_piece:
            for target_square in chess.SQUARES:
                target_piece = board.piece_at(target_square)
                if target_piece and target_piece.color != board.turn:
                    if len(board.attackers(board.turn, target_square)) > 1:  # More attackers means a skewer is possible
                        return True
        return False

    def is_isolated(self, board, square):
        file = chess.square_file(square)
        if file > 0 and board.piece_at(chess.square(chess.square_rank(square), file - 1)) and \
                board.piece_at(chess.square(chess.square_rank(square), file - 1)).piece_type == chess.PAWN:
            return False
        if file < 7 and board.piece_at(chess.square(chess.square_rank(square), file + 1)) and \
                board.piece_at(chess.square(chess.square_rank(square), file + 1)).piece_type == chess.PAWN:
            return False
        return True

    def pawn_structure_evaluation(self, board):
            evaluation = 0
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN:
                    # Isolated Pawn
                    if self.is_isolated(board, square):
                        evaluation -= 10  # Isolated pawns are weak
                    # Passed Pawn
                    if self.is_passed(board, square, piece.color):
                        evaluation += 20  # Passed pawns are valuable
                    # Doubled Pawns (on the same file)
                    if self.is_doubled(board, square, piece.color):
                        evaluation -= 5  # Doubled pawns are weak
            return evaluation

    def evaluate_passed_pawns(self, board):
        evaluation = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN:
                color = piece.color
                if self.is_passed(board, square, color):
                    # The passed pawn's value increases the further it is advanced
                    rank = chess.square_rank(square)
                    # Value of passed pawn increases with the number of ranks it has advanced
                    evaluation += (6 - rank) if color == chess.WHITE else (rank - 1)
        return evaluation

    def is_passed(self, board, square, color):
        rank = chess.square_rank(square)
        file = chess.square_file(square)
        direction = 1 if color == chess.WHITE else -1

        for r in range(rank + direction, 8 if color == chess.WHITE else -1, direction):
            for f in range(max(0, file - 1), min(7, file + 1) + 1):
                if board.piece_at(chess.square(f, r)) and board.piece_at(chess.square(f, r)).color != color:
                    return False
        return True

    def is_backward(self, board, to_square):
        """Check if a pawn move is backward (against its typical direction of movement)."""
        piece = board.piece_at(to_square)
        
        if not piece or piece.piece_type != chess.PAWN:
            return False  # Not a pawn move, so it's not backward
        
        pawn_color = piece.color
        start_rank = chess.square_rank(to_square)
        
        if pawn_color == chess.WHITE:
            # For white, pawns move from rank 2 to rank 8, so a backward move is when it goes to a lower rank
            if start_rank <= 1:  # Can't move backward if it's already at or behind its starting position
                return False
            return start_rank < chess.square_rank(to_square)
        
        elif pawn_color == chess.BLACK:
            # For black, pawns move from rank 7 to rank 1, so a backward move is when it goes to a higher rank
            if start_rank >= 6:  # Can't move backward if it's already at or behind its starting position
                return False
            return start_rank > chess.square_rank(to_square)

        return False

    def is_doubled(self, board, square, color):
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        for r in range(rank + 1, 8 if color == chess.WHITE else -1):
            if board.piece_at(chess.square(file, r)) and \
            board.piece_at(chess.square(file, r)).color == color and \
            board.piece_at(chess.square(file, r)).piece_type == chess.PAWN:
                return True
        return False

    def evaluate_center_control(self, board):
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        control = 0
        for square in center_squares:
            piece = board.piece_at(square)
            if piece:
                if piece.color == self.color:
                    control += 1  # Own piece controls the center
                else:
                    control -= 1  # Opponent's piece controls the center
        return control * 10  # Giving more weight to the center control

    def evaluate_piece_activity(self, board):
        activity = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                activity += self.piece_activity(piece, square)
        return activity

    def piece_activity(self, piece, square):
        if piece.piece_type == chess.KNIGHT:
            return 8 if square in CENTER_8_SQUARES else 4
        elif piece.piece_type == chess.BISHOP:
            return 13  # Approximate control for a bishop (diagonals)
        elif piece.piece_type == chess.ROOK:
            return 14  # Approximate control for a rook (open file or rank)
        elif piece.piece_type == chess.QUEEN:
            return 27  # Approximate control for a queen
        return 0  # For pawns or kings, this value can be adjusted
    
    def piece_square_table(self, piece_type, square, color):
        piece_square_tables = {
            chess.PAWN: [
                0, 0, 0, 0, 0, 0, 0, 0,
                50, 50, 50, 50, 50, 50, 50, 50,
                10, 10, 20, 30, 30, 20, 10, 10,
                5, 5, 10, 25, 25, 10, 5, 5,
                1, 1, 5, 25, 25, 5, 1, 1,
                0, 0, 0, 20, 20, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0
            ],
            chess.KNIGHT: [
                -50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -30, 5, 10, 15, 15, 10, 5, -30,
                -30, 0, 15, 20, 20, 15, 0, -30,
                -30, 5, 15, 20, 20, 15, 5, -30,
                -30, 0, 10, 15, 15, 10, 0, -30,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -50, -40, -30, -30, -30, -30, -40, -50
            ],
            chess.BISHOP: [
                -20, -10, 0, 5, 5, 0, -10, -20,
                -10, 0, 10, 10, 10, 10, 0, -10,
                0, 5, 10, 15, 15, 10, 5, 0,
                5, 10, 15, 20, 20, 15, 10, 5,
                5, 10, 15, 20, 20, 15, 10, 5,
                0, 5, 10, 15, 15, 10, 5, 0,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -20, -10, 0, 5, 5, 0, -10, -20
            ],
            chess.ROOK: [
                0, 0, 0, 5, 5, 0, 0, 0,
                0, 5, 10, 10, 10, 10, 5, 0,
                0, 5, 10, 15, 15, 10, 5, 0,
                0, 5, 15, 20, 20, 15, 5, 0,
                0, 5, 15, 20, 20, 15, 5, 0,
                0, 5, 10, 15, 15, 10, 5, 0,
                0, 5, 10, 10, 10, 10, 5, 0,
                0, 0, 0, 5, 5, 0, 0, 0
            ],
    
            chess.QUEEN: [
                -20, -10, 0, 5, 5, 0, -10, -20,
                -10, 0, 10, 10, 10, 10, 0, -10,
                0, 5, 10, 15, 15, 10, 5, 0,
                5, 10, 15, 20, 20, 15, 10, 5,
                5, 10, 15, 20, 20, 15, 10, 5,
                0, 5, 10, 15, 15, 10, 5, 0,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -20, -10, 0, 5, 5, 0, -10, -20
            ],
        }

        table = piece_square_tables.get(piece_type, [0] * 64)  # Default to 0 for missing types
        index = chess.square_mirror(square) if color == chess.BLACK else square
        return table[index] / 100.0  # Normalize to smaller values if needed

    def king_safety_evaluation(self, board: chess.Board) -> int:
        king_safety_score = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            
            if piece and piece.piece_type == chess.KING:
                distance_from_center = abs(chess.square_rank(square) - 4) + abs(chess.square_file(square) - 4)
                if board.is_check():  # Penalize if the king is in check
                    king_safety_score -= 50
                # King safety should consider nearby pawns
                king_safety_score += self.evaluate_surrounding_pawns(board, square)
                # Penalize kings that are open or exposed
                king_safety_score -= 5 * distance_from_center
        return king_safety_score

    def evaluate_surrounding_pawns(self, board, square):
        surrounding_pawns = 0
        directions = [-9, -8, -7, -1, 1, 7, 8, 9]  # Example directions for surrounding squares

        for direction in directions:
            new_square = square + direction
            if 0 <= new_square < 64:  # Ensure valid square index
                piece = board.piece_at(new_square)
                if piece and piece.piece_type == chess.PAWN and piece.color == board.turn:
                    surrounding_pawns += 1

        return surrounding_pawns
    
    def evaluate_piece_coordination(self, board):
        evaluation = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                evaluation += self.piece_coordination_value(board, piece, square)
        return evaluation

    def piece_coordination_value(self, board, piece, square):
        value = 0
        if piece.piece_type == chess.ROOK or piece.piece_type == chess.QUEEN:
            value += self.evaluate_rook_or_queen_coordination(board, piece, square)
        return value

    def evaluate_rook_or_queen_coordination(self, board, piece, square):
        value = 0
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        
        for target_square in chess.SQUARES:
            if board.piece_at(target_square) and board.piece_at(target_square).color == piece.color:
                if chess.square_file(target_square) == file or chess.square_rank(target_square) == rank:
                    value += 1  
        return value

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
