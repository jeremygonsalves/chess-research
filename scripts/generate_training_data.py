"""Generate training data by playing chess games with optimal moves."""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import chess
from app.game.chess_game import ChessGame


def generate_game_data(num_games: int = 10, depth: int = 15):
    """Generate training data by playing multiple games.
    
    Args:
        num_games: Number of games to generate
        depth: Search depth for optimal moves
    """
    all_games_data = []
    
    for game_num in range(num_games):
        print(f"\n{'='*60}")
        print(f"Generating Game {game_num + 1}/{num_games}")
        print(f"{'='*60}")
        
        game = ChessGame(depth=depth)
        moves_played = 0
        max_moves = 200  # Prevent infinite games
        
        while not game.board.is_game_over() and moves_played < max_moves:
            # Get optimal move
            analysis = game.get_position_analysis()
            
            if not analysis.get("best_move"):
                break
            
            # Make the optimal move
            move = analysis['best_move']
            success, message = game.make_move(move)
            
            if not success:
                print(f"Error making move: {message}")
                break
            
            moves_played += 1
            
            # Progress indicator
            if moves_played % 10 == 0:
                print(f"  Move {moves_played}: {move} (eval: {analysis['evaluation']:.2f})")
        
        # Save game data
        game_data = {
            "game_number": game_num + 1,
            "total_moves": game.move_count,
            "result": game.board.result() if game.board.is_game_over() else None,
            "moves": game.game_history,
            "final_fen": game.board.fen()
        }
        
        all_games_data.append(game_data)
        
        print(f"\nGame {game_num + 1} complete: {game.move_count} moves")
        print(f"Result: {game.board.result() if game.board.is_game_over() else 'Incomplete'}")
    
    # Save all games
    output_file = f"chess_training_data_{num_games}games.json"
    with open(output_file, 'w') as f:
        json.dump({
            "num_games": num_games,
            "total_positions": sum(len(g["moves"]) for g in all_games_data),
            "games": all_games_data
        }, f, indent=2)
    
    total_positions = sum(len(g["moves"]) for g in all_games_data)
    print(f"\n{'='*60}")
    print(f"✅ Generated {num_games} games with {total_positions} positions")
    print(f"✅ Saved to: {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    num_games = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    
    print("Chess Training Data Generator")
    print(f"Generating {num_games} games with depth {depth}")
    
    generate_game_data(num_games, depth)

