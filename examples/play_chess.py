"""Simple example of playing chess with optimal move recommendations."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.game.chess_game import ChessGame


def main():
    """Simple example game."""
    print("Starting chess game...\n")
    
    # Initialize game
    game = ChessGame(depth=15)
    
    # Display initial board
    print("Starting position:")
    print(game.get_board_diagram())
    print()
    
    # Get optimal first move
    print("Getting optimal first move...")
    analysis = game.get_position_analysis()
    print(f"Optimal move: {analysis['best_move']}")
    print(f"Evaluation: {analysis['evaluation']:.2f} pawns")
    print()
    
    # Make a few moves
    moves = ["e2e4", "e7e5", "g1f3", "b8c6"]  # Basic opening
    
    for move in moves:
        print(f"Playing: {move}")
        success, message = game.make_move(move)
        print(message)
        
        if success:
            print("\n" + game.get_board_diagram())
            
            if not game.board.is_game_over():
                analysis = game.get_position_analysis()
                print(f"\nOptimal move: {analysis['best_move']}")
                print(f"Evaluation: {analysis['evaluation']:.2f} pawns")
            print()
    
    # Export training data
    print(f"\nGame complete! Collected {game.move_count} moves.")
    game.export_training_data("example_game.json")
    print("Training data saved to example_game.json")


if __name__ == "__main__":
    main()

