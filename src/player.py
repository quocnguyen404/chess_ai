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

class AdvancedAI(AI):
    def __init__(self, color, name):
        super().__init__(color, name)
        self.base_max_depth = 5  # Max search depth
        self.eval_cache = {}  # Cache for evaluated positions
        self.base_max_move_time_cal = 2

    def get_weights(self, board):
        total_material = sum(len(board.pieces(pt, chess.WHITE)) + len(board.pieces(pt, chess.BLACK)) for pt in PIECE_VALUES)
        
        if total_material < 14:  # Endgame
            return {
                "material": 1.5,
                "king_activity": 0.5,
                "pawn_structure": 0.5,
                "pawn_majority": 0.8,
                "passed_pawn": 1.2,
                "center_control": 0.3,
                "piece_mobility": 0.2,
                "rook_activity": 0.7,
                "piece_coordination": 0.6,
                "hanging_pieces": 1.2,
                "knight_outposts": 0.7,
                "bishop_pair": 0.5,
                "tempo": 0.3,
                "open_files": 0.4,
                "weak_squares": 0.5,
                "king_safety": 1.0,
            }
        else:  # Opening or Middlegame
            return {
                "material": 1.5,
                "king_activity": 0.5,
                "pawn_structure": 0.8,
                "pawn_majority": 0.6,
                "passed_pawn": 0.8,
                "center_control": 0.8,
                "piece_mobility": 0.6,
                "rook_activity": 0.5,
                "piece_coordination": 0.6,
                "hanging_pieces": 1.2,
                "knight_outposts": 0.7,
                "bishop_pair": 0.6,
                "tempo": 0.4,
                "open_files": 0.4,
                "weak_squares": 0.5,
                "king_safety": 1.0,
            }

    def get_move(self, board):
        best_move = None
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')

        start_time = time.time()

        for depth in range(1, self.base_max_depth + 1):
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
        if board_fen in self.eval_cache:
            return self.eval_cache[board_fen]  # Return cached evaluation

        if depth == 0 or board.is_game_over():
            evaluation = self.evaluate_board(board)
            self.eval_cache[board_fen] = evaluation  # Cache evaluation
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
            self.eval_cache[board_fen] = max_eval  # Cache result
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
            self.eval_cache[board_fen] = min_eval  # Cache result
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
        weights = self.get_weights(board)

        white_material = count_material(board, chess.WHITE)
        black_material = count_material(board, chess.BLACK)

        material_score = white_material - black_material
        pawn_structure_score = self.evaluate_pawn_structure(board)
        king_safety_score = self.evaluate_king_safety(board)
        center_control_score = self.evaluate_center_control(board)
        piece_mobility_score = self.evaluate_piece_mobility(board)
        rook_activity_score = self.evaluate_rook_and_queen_activity(board)
        passed_pawn_score = self.evaluate_passed_pawn(board)
        bishop_pair_score = self.evaluate_bishop_pair(board)
        knight_outposts_score = self.evaluate_knight_outposts(board)
        tempo_score = self.evaluate_tempo(board)
        open_files_score = self.evaluate_open_files(board)
        hanging_pieces_score = self.evaluate_hanging_pieces(board)
        weak_squares_score = self.evaluate_weak_squares(board)
        piece_coordination_score = self.evaluate_piece_coordination(board)
        pawn_majority_score = self.evaluate_pawn_majority(board)

        total_score = (
            weights["material"] * material_score +
            weights["pawn_structure"] * pawn_structure_score +
            weights["king_safety"] * king_safety_score +
            weights["center_control"] * center_control_score +
            weights["piece_mobility"] * piece_mobility_score +
            weights["rook_activity"] * rook_activity_score +
            weights["passed_pawn"] * passed_pawn_score +
            weights["bishop_pair"] * bishop_pair_score +
            weights["knight_outposts"] * knight_outposts_score +
            weights["tempo"] * tempo_score +
            weights["open_files"] * open_files_score +
            weights["hanging_pieces"] * hanging_pieces_score +
            weights["weak_squares"] * weak_squares_score +
            weights["piece_coordination"] * piece_coordination_score +
            weights["pawn_majority"] * pawn_majority_score
        )

        return total_score

    
    def piece_square_table(self, piece_type, square, color):
        table = PIECE_SQUARE_TABLES.get(piece_type)
        if table is None:
            return 0  # Return 0 for piece types we don't handle

        # Get the row and column of the square
        square_index = chess.SQUARES.index(square)
        row = square_index // 8  # Row (0-7)
        col = square_index % 8  # Column (0-7)

        # For black pieces, reverse the evaluation since black's perspective is flipped
        if color == chess.BLACK:
            row = 7 - row  # Reverse the row for black pieces

        return table[row][col]
    
    def evaluate_pawn_structure(self, board):
        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)

        pawn_structure_score = 0
        # Evaluate isolated pawns (pawns with no same-color pawns on adjacent files)
        for pawn in white_pawns:
            file = chess.square_file(pawn)
            # Check for isolated pawn: no pawns on adjacent files
            # Check if there's no pawn on the left or right adjacent files
            adjacent_files = [file - 1, file + 1]
            isolated = True
            for f in adjacent_files:
                if f >= 0 and f <= 7:  # Ensure the file is within bounds (0 to 7)
                    if any(board.pieces(chess.PAWN, chess.WHITE) & chess.SquareSet(chess.BB_FILES[f])):
                        isolated = False
                        break
            if isolated:
                pawn_structure_score += 5  # Reward isolated pawns

            # Penalize isolated pawns that are under attack
            if not board.is_attacked_by(chess.BLACK, pawn):
                pawn_structure_score -= 5  # Penalize isolated pawns

        for pawn in black_pawns:
            file = chess.square_file(pawn)
            # Check for isolated pawn: no pawns on adjacent files
            # Check if there's no pawn on the left or right adjacent files
            adjacent_files = [file - 1, file + 1]
            isolated = True
            for f in adjacent_files:
                if f >= 0 and f <= 7:  # Ensure the file is within bounds (0 to 7)
                    if any(board.pieces(chess.PAWN, chess.BLACK) & chess.SquareSet(chess.BB_FILES[f])):
                        isolated = False
                        break
            if isolated:
                pawn_structure_score -= 5  # Penalize isolated pawns

            # Penalize isolated pawns that are under attack
            if not board.is_attacked_by(chess.WHITE, pawn):
                pawn_structure_score += 5  # Reward isolated pawns

        # Evaluate doubled pawns (pawns of the same color on the same file)
        for file in range(8):  # Use range(8) instead of chess.FILES
            white_pawns_in_file = [pawn for pawn in white_pawns if chess.square_file(pawn) == file]
            black_pawns_in_file = [pawn for pawn in black_pawns if chess.square_file(pawn) == file]
            
            # Penalize doubled pawns (pawns in the same file)
            if len(white_pawns_in_file) > 1:
                pawn_structure_score -= 10  # Penalize doubled pawns
            if len(black_pawns_in_file) > 1:
                pawn_structure_score += 10  # Reward doubled pawns for Black

        # Evaluate backward pawns (pawns behind the rest of the pawns in the same file)
        for pawn in white_pawns:
            file = chess.square_file(pawn)
            # Check if the pawn is backward (behind other pawns on adjacent files)
            if file < 7:  # Ensure not the last file
                if not any(board.pieces(chess.PAWN, chess.WHITE) & chess.SquareSet(chess.BB_FILES[file + 1])):
                    pawn_structure_score -= 10  # Penalize backward pawns

        for pawn in black_pawns:
            file = chess.square_file(pawn)
            # Check if the pawn is backward (behind other pawns on adjacent files)
            if file < 7:  # Ensure not the last file
                if not any(board.pieces(chess.PAWN, chess.BLACK) & chess.SquareSet(chess.BB_FILES[file + 1])):
                    pawn_structure_score += 10  # Reward backward pawns

        return pawn_structure_score
    
    def evaluate_king_safety(self, board):
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)

        king_safety_score = 0

        # Phase-aware king safety evaluation
        total_material = sum(
            len(board.pieces(pt, chess.WHITE)) + len(board.pieces(pt, chess.BLACK))
            for pt in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
        )

        # Opening phase: Encourage castling and minimal safety checks
        if total_material > 20:
            king_safety_score += self.reward_castling(white_king, chess.WHITE)
            king_safety_score += self.reward_castling(black_king, chess.BLACK)

        # Middlegame and endgame: Evaluate shields and safety more rigorously
        else:
            king_safety_score += self.evaluate_pawn_shield(board, white_king, chess.WHITE)
            king_safety_score += self.evaluate_pawn_shield(board, black_king, chess.BLACK)

        return king_safety_score

    def reward_castling(self, board, king_pos, color):
        castling_bonus = 0
        if color == chess.WHITE:
            if king_pos == chess.G1 or king_pos == chess.C1:  # Castling squares for White
                castling_bonus += 30
            elif king_pos == chess.E1 and not board.has_castling_rights(chess.WHITE):  
                # Penalize uncastled king if castling rights are lost
                castling_bonus -= 10
        else:
            if king_pos == chess.G8 or king_pos == chess.C8:  # Castling squares for Black
                castling_bonus += 30
            elif king_pos == chess.E8 and not board.has_castling_rights(chess.BLACK):
                castling_bonus -= 10

        return castling_bonus


    def evaluate_pawn_shield(self, board, king_square, color):
        score = 0

        # Determine pawn shield squares based on the king's position
        direction = 1 if color == chess.WHITE else -1
        king_rank = chess.square_rank(king_square)
        king_file = chess.square_file(king_square)

        # Potential pawn shield squares (front and diagonals)
        shield_squares = [
            chess.square(king_file - 1, king_rank + direction) if 0 <= king_file - 1 <= 7 else None,
            chess.square(king_file, king_rank + direction) if 0 <= king_file <= 7 else None,
            chess.square(king_file + 1, king_rank + direction) if 0 <= king_file + 1 <= 7 else None,
        ]

        for sq in shield_squares:
            if sq is not None and board.piece_at(sq) and board.piece_at(sq).piece_type == chess.PAWN:
                piece_color = board.piece_at(sq).color
                if piece_color == color:
                    score += 10  # Reward pawns that shield the king

        return score

    def evaluate_center_control(self, board):
        center_control_score = 0

        # Define the center squares
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        
        # Create a lookup table for piece values in the center (positive for White, negative for Black)
        piece_value_table = {
            chess.PAWN: 10,
            chess.KNIGHT: 5,
            chess.BISHOP: 5,
            chess.QUEEN: 10,
            chess.ROOK: 3,
            chess.KING: -5  # Penalize kings in the center, especially early in the game
        }

        # Evaluate pieces in the center for both players
        for square in center_squares:
            piece = board.piece_at(square)
            if piece is not None:
                if piece.color == board.turn:  # White's turn or Black's turn
                    center_control_score += piece_value_table.get(piece.piece_type, 0)
                else:
                    center_control_score -= piece_value_table.get(piece.piece_type, 0)

        # Evaluate pawns supporting the center from a distance
        supporting_pawn_squares = [chess.D3, chess.E3, chess.D6, chess.E6]
        for square in supporting_pawn_squares:
            piece = board.piece_at(square)
            if piece is not None and piece.piece_type == chess.PAWN:
                if piece.color == board.turn:  # Reward White pawns, penalize Black pawns
                    center_control_score += 3  # Reward pawns supporting the center
                else:
                    center_control_score -= 3  # Penalize pawns from the opponent supporting the center

        control_bonus = 0
        for square in center_squares:
            if board.is_attacked_by(board.turn, square):
                control_bonus += 2  # Bonus for controlling the square
        center_control_score += control_bonus

        extended_supporting_pawn_squares = [chess.C3, chess.F3, chess.C6, chess.F6]
        for square in extended_supporting_pawn_squares:
            piece = board.piece_at(square)
            if piece is not None and piece.piece_type == chess.PAWN:
                if piece.color == board.turn:
                    center_control_score += 3  # Reward supporting pawns
                else:
                    center_control_score -= 3  # Penalize opponent's supporting pawns

        return center_control_score

    def evaluate_piece_mobility(self, board):
        mobility_score = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                color = piece.color
                piece_type = piece.piece_type
                # Calculate the number of legal moves for each piece
                if piece_type == chess.PAWN:
                    mobility_score += self.pawn_mobility(square, piece, board)
                elif piece_type == chess.KNIGHT:
                    mobility_score += self.knight_mobility(square, piece, board)
                elif piece_type == chess.BISHOP:
                    mobility_score += self.bishop_mobility(square, piece, board)
                elif piece_type == chess.ROOK:
                    mobility_score += self.rook_mobility(square, piece, board)
                elif piece_type == chess.QUEEN:
                    mobility_score += self.queen_mobility(square, piece, board)
                elif piece_type == chess.KING:
                    mobility_score += self.king_mobility(square, piece, board)

                # If it's the opponent's turn, subtract the mobility score
                if color != board.turn:
                    mobility_score -= mobility_score

        return mobility_score

    def pawn_mobility(self, square, piece, board):
        mobility_score = 0
        if piece.piece_type == chess.PAWN:
            # Ensure pawns on rank 1 (second rank) can move two squares
            if piece.color == chess.WHITE:
                if chess.square_rank(square) == 1:  # On the second rank
                    # Check if two squares ahead are open (rank 3 for white pawns)
                    if 0 <= square + 16 < 64 and board.piece_at(square + 16) is None:
                        mobility_score += 1  # Reward double pawn move
                # Check for single-square moves (standard pawn move)
                if 0 <= square + 8 < 64 and board.piece_at(square + 8) is None:
                    mobility_score += 1  # Reward single-square move
            elif piece.color == chess.BLACK:
                if chess.square_rank(square) == 6:  # On the second-to-last rank (7th rank for black pawns)
                    # Check if two squares ahead are open (rank 5 for black pawns)
                    if 0 <= square - 16 < 64 and board.piece_at(square - 16) is None:
                        mobility_score += 1  # Reward double pawn move
                # Check for single-square moves (standard pawn move)
                if 0 <= square - 8 < 64 and board.piece_at(square - 8) is None:
                    mobility_score += 1  # Reward single-square move

        return mobility_score


    def rook_mobility(self, square, piece, board):
        mobility = 0
        for direction in ROOK_DIRECTIONS:
            target_square = square
            while True:
                target_square += direction
                if not square_is_on_board(target_square):  # Check if the target square is within the board
                    break
                if board.piece_at(target_square) is None:  # Empty square
                    mobility += 1
                else:  # Blocked by a piece
                    break
        return mobility

    def bishop_mobility(self, square, piece, board):
        mobility = 0
        for direction in BISHOP_DIRECTIONS:
            target_square = square
            while True:
                target_square += direction
                if not square_is_on_board(target_square):  # Check if the target square is within the board
                    break
                if board.piece_at(target_square) is None:  # Empty square
                    mobility += 1
                else:  # Blocked by a piece
                    break
        return mobility

    def knight_mobility(self, square, piece, board):
        mobility = 0
        for move in KNIGHT_MOVES:
            target_square = square + move
            if square_is_on_board(target_square) and board.piece_at(target_square) is None:
                mobility += 1
        return mobility

    def queen_mobility(self, square, piece, board):
        mobility = 0
        mobility += self.rook_mobility(square, piece, board)  # Rook-like moves
        mobility += self.bishop_mobility(square, piece, board)  # Bishop-like moves
        return mobility

    def king_mobility(self, square, piece, board):
        mobility = 0
        for move in KING_MOVES:
            target_square = square + move
            if square_is_on_board(target_square) and board.piece_at(target_square) is None:
                mobility += 1
        return mobility

    def evaluate_rook_and_queen_activity(self, board):
        activity_score = 0

        # Loop through all pieces on the board
        for square in range(64):
            piece = board.piece_at(square)
            
            if piece is None:
                continue

            # Evaluate activity for rooks and queens
            if piece.piece_type == chess.ROOK:
                activity_score += self.rook_activity(square, piece, board)
            elif piece.piece_type == chess.QUEEN:
                activity_score += self.queen_activity(square, piece, board)

        return activity_score
    
    def rook_activity(self, square, piece, board):
        activity_score = 0
        
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        
        # Check if the rook is placed on an open or semi-open file
        if all(board.piece_at(chess.square(r, file)) is None or board.piece_at(chess.square(r, file)).color != piece.color for r in range(8)):
            activity_score += 1  # Reward rooks on open files
        elif all(board.piece_at(chess.square(r, file)) is None or board.piece_at(chess.square(r, file)).color == piece.color for r in range(8)):
            activity_score += 0.5  # Reward rooks on semi-open files

        # Check if the rook is controlling important squares (like central ranks)
        if rank in [3, 4, 5]:
            activity_score += 0.5  # Reward rooks on central ranks

        return activity_score

    def queen_activity(self, square, piece, board):
        activity_score = 0
        
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        
        # Reward the queen if it is in or near the center
        if square in center_squares:
            activity_score += 2
        elif chess.square_rank(square) in [3, 4] and chess.square_file(square) in [3, 4]:
            activity_score += 1
        
        # Evaluate squares controlled by the queen (like open lines, diagonals, etc.)
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        
        # Reward queens controlling important files or diagonals
        if all(board.piece_at(chess.square(r, file)) is None for r in range(8)):
            activity_score += 1  # Reward queens on open files
        if all(board.piece_at(chess.square(rank, f)) is None for f in range(8)):
            activity_score += 1  # Reward queens on open ranks
        if all(board.piece_at(chess.square(r, c)) is None for r, c in zip(range(8), range(8))):  # Example diagonal control
            activity_score += 0.5  # Reward queens controlling diagonals

        return activity_score

    def evaluate_passed_pawn(self, board):
        passed_pawn_score = 0
        color = board.turn

        # Loop through all squares to find passed pawns for the given color
        for square in range(64):
            piece = board.piece_at(square)
            
            if piece is None or piece.piece_type != chess.PAWN or piece.color != color:
                continue

            # Check for passed pawn and add the score based on its position
            if self.is_passed_pawn(board, square, piece.color):
                passed_pawn_score += self.passed_pawn_position_score(square, piece.color)

        return passed_pawn_score

    def is_passed_pawn(self, board, square, color):
        file = chess.square_file(square)
        
        # Check for opponent pawns on the same or adjacent files above the current pawn
        for rank in range(chess.square_rank(square) + 1, 8):
            opponent_pawns = board.pieces(chess.PAWN, chess.BLACK if color == chess.WHITE else chess.WHITE)
            for opponent_pawn_square in opponent_pawns:
                opponent_file = chess.square_file(opponent_pawn_square)
                opponent_rank = chess.square_rank(opponent_pawn_square)

                # If an opponent pawn is on the same or adjacent file and ahead, the pawn is blocked
                if opponent_rank > rank and opponent_file in [file - 1, file, file + 1]:
                    return False
        return True

    def passed_pawn_position_score(self, square, color):
        rank = chess.square_rank(square)
        
        # Reward passed pawns as they advance towards promotion
        score = 0
        if color == chess.WHITE:
            score = rank  # White pawns get higher score as they advance to rank 8
        elif color == chess.BLACK:
            score = 7 - rank  # Black pawns get higher score as they advance to rank 1
        
        return score

    def evaluate_bishop_pair(self, board):
        # Count the number of bishops for both colors
        white_bishops = board.pieces(chess.BISHOP, chess.WHITE)
        black_bishops = board.pieces(chess.BISHOP, chess.BLACK)
        
        score = 0

        # Evaluate bishop pair for White and Black
        if len(white_bishops) == 2:
            score += 30  # A bishop pair is generally a strong advantage
            score += self.bishop_position_score(white_bishops, board)  # Position-based score for White's bishops
        if len(black_bishops) == 2:
            score -= 30  # A bishop pair for Black is a disadvantage for White
            score -= self.bishop_position_score(black_bishops, board)  # Position-based score for Black's bishops

        return score

    def bishop_position_score(self, bishops, board):
        score = 0

        for bishop_square in bishops:
            # Get bishop's position
            rank = chess.square_rank(bishop_square)
            file = chess.square_file(bishop_square)

            # Add score for central positions
            if rank in [3, 4] and file in [3, 4]:  # The center squares are D4, E4, D5, E5
                score += 5

            # Evaluate open diagonals: bishops on diagonals with no pawns
            if self.is_bishop_on_open_diagonal(bishop_square, board):
                score += 10  # A bishop on an open diagonal is stronger

            # Bishops on the long diagonals (a1-h8 and h1-a8) are usually stronger
            if bishop_square in [chess.A1, chess.H1, chess.A8, chess.H8]:
                score += 5

        return score

    def is_bishop_on_open_diagonal(self, bishop_square, board):
        # Check if the bishop is on an open diagonal (no pawns on the diagonal)
        directions = [(-1, -1), (1, 1), (-1, 1), (1, -1)]  # All 4 diagonal directions
        for direction in directions:
            file, rank = chess.square_file(bishop_square), chess.square_rank(bishop_square)

            # Explore the diagonal in the direction
            for i in range(1, 8):
                # Calculate new square coordinates along the diagonal
                new_file = file + direction[0] * i
                new_rank = rank + direction[1] * i

                # Check if the new square is within bounds
                if not square_is_on_board(chess.square(new_file, new_rank)):
                    break  # Stop if the square is off the board

                # Check if there's a pawn on this square
                piece = board.piece_at(chess.square(new_file, new_rank))
                if piece and piece.piece_type == chess.PAWN:
                    return False  # A pawn is blocking the diagonal

        return True  # No pawns found, the diagonal is open

    def evaluate_weak_squares(self, board):
        score = 0

        # Loop through all squares on the board
        for square in range(64):
            piece = board.piece_at(square)

            if piece is None:
                continue

            # Check for isolated pawns
            if piece.piece_type == chess.PAWN:
                file = chess.square_file(square)
                rank = chess.square_rank(square)

                # Check if the pawn is isolated (no friendly pawns in adjacent files)
                if not self.is_pawn_supported(board, square, piece.color):
                    # Penalize isolated pawns
                    score += -10 if piece.color == chess.WHITE else 10

            # Additional evaluation for weak squares with other pieces can be added here
            # For example, unprotected squares or backward pawns could also be assessed.

        return score

    def is_pawn_supported(self, board, square, color):
        file = chess.square_file(square)

        # Determine which pawns to check based on the color
        if color == chess.WHITE:
            supporting_pawns = board.pieces(chess.PAWN, chess.WHITE)
        else:
            supporting_pawns = board.pieces(chess.PAWN, chess.BLACK)
        
        # Check if there is a supporting pawn on adjacent files
        for supporting_pawn_square in supporting_pawns:
            supporting_file = chess.square_file(supporting_pawn_square)
            supporting_rank = chess.square_rank(supporting_pawn_square)

            # Only check pawns that are on the same rank or one rank behind
            if abs(supporting_file - file) <= 1 and supporting_rank == chess.square_rank(square):
                return True  # Pawn is supported by a neighboring pawn

        return False  # Pawn is isolated

    def evaluate_piece_coordination(self, board):
        score = 0

        # Knight coordination: Knights that support each other are valuable
        white_knights = board.pieces(chess.KNIGHT, chess.WHITE)
        black_knights = board.pieces(chess.KNIGHT, chess.BLACK)
        
        score += self.knight_coordination_score(white_knights)
        score -= self.knight_coordination_score(black_knights)

        # Rook coordination: Rooks on the same file or rank are stronger
        white_rooks = board.pieces(chess.ROOK, chess.WHITE)
        black_rooks = board.pieces(chess.ROOK, chess.BLACK)
        
        score += self.rook_coordination_score(white_rooks)
        score -= self.rook_coordination_score(black_rooks)

        # Queen coordination: Queens are stronger when they coordinate with other pieces
        white_queens = board.pieces(chess.QUEEN, chess.WHITE)
        black_queens = board.pieces(chess.QUEEN, chess.BLACK)

        score += self.queen_coordination_score(white_queens)
        score -= self.queen_coordination_score(black_queens)

        # Bishop coordination: Bishops on the same diagonal work together
        white_bishops = board.pieces(chess.BISHOP, chess.WHITE)
        black_bishops = board.pieces(chess.BISHOP, chess.BLACK)

        score += self.bishop_coordination_score(white_bishops)
        score -= self.bishop_coordination_score(black_bishops)

        return score

    def knight_coordination_score(self, knights):
        score = 0
        knight_positions = list(knights)

        # Check if knights are supporting each other
        for i in range(len(knight_positions)):
            for j in range(i + 1, len(knight_positions)):
                knight_1 = knight_positions[i]
                knight_2 = knight_positions[j]

                # Check if the knights are within range of each other (distance <= 2)
                if chess.square_distance(knight_1, knight_2) <= 2:
                    score += 5  # Reward coordination between knights

        return score

    def rook_coordination_score(self, rooks):
        score = 0
        rook_positions = list(rooks)

        # Check if rooks are on the same file or rank
        for i in range(len(rook_positions)):
            for j in range(i + 1, len(rook_positions)):
                rook_1 = rook_positions[i]
                rook_2 = rook_positions[j]

                if chess.square_file(rook_1) == chess.square_file(rook_2) or chess.square_rank(rook_1) == chess.square_rank(rook_2):
                    score += 10  # Reward rooks on the same file or rank

        return score

    def queen_coordination_score(self, queens):
        score = 0
        queen_positions = list(queens)

        # Check if queens are supporting each other or other pieces
        for i in range(len(queen_positions)):
            for j in range(i + 1, len(queen_positions)):
                queen_1 = queen_positions[i]
                queen_2 = queen_positions[j]

                # Reward queens coordinating closely
                if chess.square_distance(queen_1, queen_2) <= 2:
                    score += 7  # Reward queens coordinating closely

        return score

    def bishop_coordination_score(self, bishops):
        score = 0
        bishop_positions = list(bishops)

        # Check if bishops are on the same diagonal
        for i in range(len(bishop_positions)):
            for j in range(i + 1, len(bishop_positions)):
                bishop_1 = bishop_positions[i]
                bishop_2 = bishop_positions[j]

                # Check if bishops are on the same diagonal
                if abs(chess.square_rank(bishop_1) - chess.square_rank(bishop_2)) == abs(chess.square_file(bishop_1) - chess.square_file(bishop_2)):
                    score += 5  # Reward bishops on the same diagonal

        return score

    def evaluate_pawn_majority(self, board):
        score = 0

        # Split the board into two parts: Kingside (files f, g, h) and Queenside (files a, b, c, d)
        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)

        white_queenside = sum(1 for pawn in white_pawns if chess.square_file(pawn) < 4)
        white_kingside = sum(1 for pawn in white_pawns if chess.square_file(pawn) >= 4)

        black_queenside = sum(1 for pawn in black_pawns if chess.square_file(pawn) < 4)
        black_kingside = sum(1 for pawn in black_pawns if chess.square_file(pawn) >= 4)

        # Add score based on pawn majority difference
        queenside_majority_diff = white_queenside - black_queenside
        kingside_majority_diff = white_kingside - black_kingside

        # Reward/penalize based on the difference in pawn numbers on each side
        score += queenside_majority_diff * 5  # Adjust the multiplier for more granular scoring
        score += kingside_majority_diff * 5  # Adjust the multiplier for more granular scoring

        return score

    def evaluate_knight_outposts(self, board):
        score = 0

        # Get all knights for both colors
        white_knights = board.pieces(chess.KNIGHT, chess.WHITE)
        black_knights = board.pieces(chess.KNIGHT, chess.BLACK)

        # Check white knights
        for knight_square in white_knights:
            rank = chess.square_rank(knight_square)

            # Ideal outpost squares are on the 5th and 6th ranks (for white, rank 3 and 4 for black)
            if rank in [3, 4]:
                score += 10  # Reward knight on ideal outpost
            if self.is_knight_on_safe_square(board, knight_square, chess.WHITE):
                score += 5  # Reward knights that are not easily attacked

        # Check black knights
        for knight_square in black_knights:
            rank = chess.square_rank(knight_square)

            # Ideal outpost squares are on the 5th and 6th ranks (for white, rank 3 and 4 for black)
            if rank in [3, 4]:
                score -= 10  # Penalize opponent's knights on ideal outposts
            if self.is_knight_on_safe_square(board, knight_square, chess.BLACK):
                score -= 5  # Penalize opponent's knights that are not easily attacked

        return score

    def is_knight_on_safe_square(self, board, knight_square, knight_color):
        file = chess.square_file(knight_square)
        rank = chess.square_rank(knight_square)

        # A knight on an outpost should not be attacked by an opponent pawn
        opponent_color = chess.BLACK if knight_color == chess.WHITE else chess.WHITE
        opponent_pawns = board.pieces(chess.PAWN, opponent_color)

        # Check if the knight is under attack by an opponent pawn (only consider pawns that can attack the knight's position)
        for opponent_pawn_square in opponent_pawns:
            opponent_pawn_file = chess.square_file(opponent_pawn_square)
            opponent_pawn_rank = chess.square_rank(opponent_pawn_square)

            # Check if the opponent's pawn can attack the knight
            if knight_color == chess.WHITE:
                if opponent_pawn_rank == rank + 1 and abs(opponent_pawn_file - file) == 1:
                    return False  # Knight is under attack by an opponent pawn
            else:
                if opponent_pawn_rank == rank - 1 and abs(opponent_pawn_file - file) == 1:
                    return False  # Knight is under attack by an opponent pawn

        return True  # The knight is on a safe square

    def evaluate_tempo(self, board):
        score = 0

        if board.turn == chess.WHITE:
            # Reward for White moving pieces out in a natural development
            score += 10  # Reward for having the next move
        else:
            # Penalize Black for reacting to White's moves
            score -= 10  # Penalize Black for having to react to White's moves

        # Track moves that seem inefficient
        for move in board.legal_moves:
            piece = board.piece_at(move.from_square)
            if piece and piece.piece_type == chess.PAWN:
                # Penalize for moving pawns unnecessarily (moving pawns multiple times in the opening can waste tempo)
                if self.is_pawn_moved_twice(board, move.from_square):
                    score -= 5  # Penalize for moving the same pawn twice

            if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
                # Penalize repeated moves (if the same piece moves more than once in the opening)
                if self.has_piece_moved_twice(board, piece):
                    score -= 5  # Penalize for moving the same piece twice
        return score

    def is_pawn_moved_twice(self, board, pawn_square):
        # Check if a pawn has already moved once (and now moves a second time)
        if chess.square_rank(pawn_square) == 6 or chess.square_rank(pawn_square) == 1:
            # Pawn is on its starting position, check if it's moved
            for move in board.move_stack:
                if move.from_square == pawn_square and move.to_square == pawn_square + 8:
                    return True  # Pawn has moved twice
        return False

    def has_piece_moved_twice(self, board, piece):
        # Check if a piece has moved twice in the opening phase
        move_count = 0
        for move in board.move_stack:
            if board.piece_at(move.from_square) == piece:
                move_count += 1
            if move_count > 1:
                return True
        return False

    def evaluate_open_files(self, board):
        score = 0

        # Loop through each file (0-7)
        for file in range(8):
            # Get the pawns for both sides on the current file
            white_pawns = board.pieces(chess.PAWN, chess.WHITE).intersection(chess.BB_FILES[file])
            black_pawns = board.pieces(chess.PAWN, chess.BLACK).intersection(chess.BB_FILES[file])

            # Check if the file is open (no pawns) or semi-open (one color has pawns)
            is_open_file = len(white_pawns) == 0 and len(black_pawns) == 0
            is_semi_open_file = (len(white_pawns) == 0 and len(black_pawns) > 0) or (len(white_pawns) > 0 and len(black_pawns) == 0)

            # For open files, reward rooks and queens
            if is_open_file:
                score += self.evaluate_file_control(board, file, chess.WHITE)
                score -= self.evaluate_file_control(board, file, chess.BLACK)
            elif is_semi_open_file:
                if len(white_pawns) == 0:
                    score = score + self.evaluate_file_control(board, file, chess.WHITE)
                else:
                    score = score - self.evaluate_file_control(board, file, chess.BLACK)

        return score

    def evaluate_file_control(self, board, file, color):
        score = 0

        # Get rooks and queens for the given color on the specified file
        pieces = board.pieces(chess.ROOK, color).union(board.pieces(chess.QUEEN, color))

        for piece_square in pieces:
            if chess.square_file(piece_square) == file:
                # Reward pieces controlling open or semi-open files
                score += 10

                # Optionally add a rank-based bonus for rooks/queens in advanced positions
                rank = chess.square_rank(piece_square)
                if color == chess.WHITE:
                    score += 2 * (7 - rank)  # Higher rank = more control for White
                else:
                    score += 2 * rank  # Higher rank = more control for Black

        return score if score != 0 else 0  # Ensure a numeric return value

    def evaluate_hanging_pieces(self, board):
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE and not board.is_attacked_by(chess.WHITE, square):
                    if board.is_attacked_by(chess.BLACK, square):
                        score -= PIECE_VALUES[piece.piece_type]
                elif piece.color == chess.BLACK and not board.is_attacked_by(chess.BLACK, square):
                    if board.is_attacked_by(chess.WHITE, square):
                        score += PIECE_VALUES[piece.piece_type]
        return score


    
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
