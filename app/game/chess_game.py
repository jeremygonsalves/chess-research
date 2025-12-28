"""Interactive chess game with optimal move recommendations."""

import chess
import chess.engine
from typing import Optional, Tuple, Dict, List
from datetime import datetime
import json


class ChessGame:
    """Interactive chess game that recommends optimal moves."""
    
    def __init__(self, engine_path: str = "stockfish", depth: int = 15):
        """Initialize chess game.
        
        Args:
            engine_path: Path to Stockfish executable
            depth: Search depth for optimal move calculation
        """
        self.board = chess.Board()
        self.engine_path = engine_path
        self.depth = depth
        self.game_history: List[Dict] = []
        self.move_count = 0
        
    def get_optimal_move(self, time_limit: Optional[float] = None) -> Optional[chess.Move]:
        """Get the optimal move for the current position.
        
        Args:
            time_limit: Optional time limit in seconds
            
        Returns:
            Best move or None if game is over
        """
        if self.board.is_game_over():
            return None
            
        try:
            with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
                limit = chess.engine.Limit(depth=self.depth)
                if time_limit:
                    limit = chess.engine.Limit(time=time_limit)
                    
                result = engine.play(self.board, limit)
                return result.move
        except Exception as e:
            print(f"Error getting optimal move: {e}")
            return None
    
    def get_position_analysis(self, time_limit: Optional[float] = None) -> Dict:
        """Get detailed analysis of the current position.
        
        Args:
            time_limit: Optional time limit in seconds
            
        Returns:
            Dictionary with evaluation, best move, and principal variation
        """
        if self.board.is_game_over():
            return {
                "game_over": True,
                "result": self.board.result(),
                "evaluation": None,
                "best_move": None,
                "pv": None
            }
        
        try:
            with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
                limit = chess.engine.Limit(depth=self.depth)
                if time_limit:
                    limit = chess.engine.Limit(time=time_limit)
                
                info = engine.analyse(self.board, limit)
                result = info["score"].white()
                
                # Get evaluation in centipawns
                eval_cp = result.score()
                if eval_cp is None:
                    mate_score = result.mate()
                    if mate_score is not None:
                        eval_cp = 30000 if mate_score > 0 else -30000
                    else:
                        eval_cp = 0
                
                # Get principal variation
                pv_moves = info.get("pv", [])
                pv = [str(move) for move in pv_moves[:10]]
                best_move = str(pv_moves[0]) if pv_moves else None
                
                return {
                    "game_over": False,
                    "evaluation": eval_cp / 100.0,  # Convert to pawns
                    "best_move": best_move,
                    "pv": pv,
                    "fen": self.board.fen(),
                    "nodes": info.get("nodes", None),
                }
        except Exception as e:
            return {
                "game_over": False,
                "error": str(e),
                "evaluation": None,
                "best_move": None,
                "pv": None
            }
    
    def make_move(self, move_uci: str) -> Tuple[bool, str]:
        """Make a move on the board.
        
        Args:
            move_uci: Move in UCI format (e.g., "e2e4")
            
        Returns:
            Tuple of (success, message)
        """
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                # Get optimal move BEFORE making the move (for accuracy analysis)
                fen_before = self.board.fen()
                analysis_before = self.get_position_analysis()
                optimal_move_before = analysis_before.get("best_move") if analysis_before else None
                evaluation_before = analysis_before.get("evaluation") if analysis_before else None
                
                # Now make the move
                self.board.push(move)
                self.move_count += 1
                
                # Record move with optimal move for the position BEFORE this move
                position_data = {
                    "move_number": self.move_count,
                    "move_played": move_uci,
                    "fen_before": fen_before,
                    "fen_after": self.board.fen(),
                    "optimal_move_for_position": optimal_move_before,  # Optimal move for position before this move
                    "evaluation_before": evaluation_before,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                
                # Get optimal move for new position (opponent's turn) - for next move
                if not self.board.is_game_over():
                    analysis = self.get_position_analysis()
                    position_data["optimal_move"] = analysis.get("best_move")  # For opponent's next move
                    position_data["evaluation"] = analysis.get("evaluation")
                
                self.game_history.append(position_data)
                
                return True, "Move successful"
            else:
                return False, f"Illegal move: {move_uci}"
        except ValueError:
            return False, f"Invalid move format: {move_uci}"
    
    def get_legal_moves(self) -> List[str]:
        """Get list of legal moves in UCI format."""
        return [move.uci() for move in self.board.legal_moves]
    
    def export_training_data(self, filename: str = "training_data.json"):
        """Export game history as training data.
        
        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump({
                "game_history": self.game_history,
                "total_moves": self.move_count,
                "final_fen": self.board.fen(),
                "result": self.board.result() if self.board.is_game_over() else None
            }, f, indent=2)
        
        print(f"Training data exported to {filename}")
    
    def reset(self):
        """Reset the game to starting position."""
        self.board = chess.Board()
        self.game_history = []
        self.move_count = 0
    
    def get_board_diagram(self) -> str:
        """Get ASCII representation of the board."""
        return str(self.board)
    
    def analyze_game_accuracy(self) -> Dict:
        """Analyze the accuracy of moves played vs optimal moves.
        
        This compares each move you played to the optimal move Stockfish
        recommended for that position (stored in optimal_move_for_position).
        
        Returns:
            Dictionary with accuracy statistics
        """
        if not self.game_history:
            return {
                "total_positions": 0,
                "accuracy": 0.0,
                "optimal_moves": 0,
                "suboptimal_moves": 0,
                "move_details": [],
                "accuracy_percentage": "0.00%"
            }
        
        optimal_count = 0
        suboptimal_count = 0
        move_details = []
        
        # Analyze each move in the game
        for move_data in self.game_history:
            move_played = move_data.get("move_played")
            # Check both possible field names for backward compatibility
            optimal_move = move_data.get("optimal_move_for_position") or move_data.get("optimal_move")
            
            if optimal_move and move_played:
                is_optimal = (move_played == optimal_move)
                
                if is_optimal:
                    optimal_count += 1
                else:
                    suboptimal_count += 1
                
                move_details.append({
                    "move_number": move_data.get("move_number"),
                    "move_played": move_played,
                    "optimal_move": optimal_move,
                    "is_optimal": is_optimal,
                    "evaluation_before": move_data.get("evaluation_before") or move_data.get("evaluation")
                })
        
        total_positions = optimal_count + suboptimal_count
        accuracy = optimal_count / total_positions if total_positions > 0 else 0.0
        
        return {
            "total_positions": total_positions,
            "accuracy": accuracy,
            "optimal_moves": optimal_count,
            "suboptimal_moves": suboptimal_count,
            "move_details": move_details,
            "accuracy_percentage": f"{accuracy * 100:.2f}%"
        }

