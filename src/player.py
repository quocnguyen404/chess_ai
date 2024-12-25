import random
import chess

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 100,  
}

# class Player:
#     def __init__(self, color, name):
#         self.name = name
#         self.color = color

#     def get_move(self, board):
#         pass

def count_material(board: chess.Board, color: chess.Color) -> int:
    material = 0
    for piece_type in PIECE_VALUES:
        material += len(board.pieces(piece_type, color)) * PIECE_VALUES[piece_type]
    return material

def evaluate_board(board: chess.Board) -> int:
    if board.is_checkmate():
        return 10000 if board.turn else -10000
    if board.is_stalemate():
        return 0
    if board.is_insufficient_material():
        return 0
    white_material = count_material(board, chess.WHITE)
    black_material = count_material(board, chess.BLACK)
    return white_material - black_material

class AI:
    def __init__(self, color, name):
        self.name = name
        self.color = color
    
    def get_move(self, board):
        pass

    def clear(self):
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
            return 5

    def alpha_beta(self, board, depth, alpha, beta, maximizing_player):
        """Perform Alpha-Beta pruning."""
        if depth == 0 or board.is_game_over():
            return evaluate_board(board)

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

#stockfish
class AdvancedAI(AI):
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
