import random
import chess

class Player:
    def __init__(self, color, name):
        self.name = name
        self.color = color

    def get_move(self, board):
        pass

class AI(Player):
    def __init__(self, color, name):
        super().__init__(color, name)
    
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
        self.engine_path =  "engine/stockfish.exe"

    def evaluate(self, board):
        with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
            info = engine.analyse(board, chess.engine.Limit(time=0.1))
            score = info["score"].relative
            if score.is_mate():
                return 10000 if score.mate() > 0 else -10000
            else:
                return score.score()
            
    def alpha_beta(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.is_game_over():
            return self.evaluate_position(board)

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

    def get_move(self, board):
        best_move = None
        max_eval = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        for move in board.legal_moves:
            board.push(move)
            eval = self.alpha_beta(board, self.max_depth - 1, alpha, beta, False)
            board.pop()

            if eval > max_eval:
                max_eval = eval
                best_move = move

        return best_move

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
