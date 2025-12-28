"""Interactive command-line chess game."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.game.chess_game import ChessGame


def print_help():
    """Print help information."""
    print("\nCommands:")
    print("  move <move>    - Make a move (e.g., 'move e2e4')")
    print("  best           - Show optimal move for current position")
    print("  analyze        - Show detailed position analysis")
    print("  board          - Display board")
    print("  legal          - Show legal moves")
    print("  reset          - Reset game")
    print("  save <file>    - Save training data")
    print("  quit           - Exit game")
    print()


def main():
    """Run interactive chess game."""
    print("=" * 60)
    print("Chess Game with Optimal Move Recommendations")
    print("=" * 60)
    print("\nGoal: Collect positions and optimal moves for ML training")
    print()
    
    # Initialize game
    try:
        game = ChessGame(depth=15)
    except Exception as e:
        print(f"Error initializing Stockfish: {e}")
        print("Make sure Stockfish is installed: brew install stockfish")
        sys.exit(1)
    
    print("Game started! Type 'help' for commands.\n")
    print(game.get_board_diagram())
    print()
    
    while True:
        try:
            command = input("chess> ").strip().split()
            
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == "quit" or cmd == "exit":
                print("Goodbye!")
                break
            
            elif cmd == "help":
                print_help()
            
            elif cmd == "move":
                if len(command) < 2:
                    print("Usage: move <move> (e.g., 'move e2e4')")
                    continue
                
                move = command[1]
                success, message = game.make_move(move)
                print(message)
                
                if success:
                    print("\n" + game.get_board_diagram())
                    print()
                    
                    if game.board.is_game_over():
                        print(f"Game over! Result: {game.board.result()}")
                        print(f"Total moves collected: {game.move_count}")
                    else:
                        # Show optimal move for new position
                        analysis = game.get_position_analysis()
                        if analysis.get("best_move"):
                            print(f"Optimal move: {analysis['best_move']}")
                            print(f"Evaluation: {analysis['evaluation']:.2f} pawns")
                        print()
            
            elif cmd == "best":
                if game.board.is_game_over():
                    print("Game is over!")
                    continue
                
                analysis = game.get_position_analysis()
                if analysis.get("best_move"):
                    print(f"Optimal move: {analysis['best_move']}")
                    print(f"Evaluation: {analysis['evaluation']:.2f} pawns")
                    if analysis.get("pv"):
                        print(f"Principal variation: {' → '.join(analysis['pv'][:5])}")
                else:
                    print("Could not determine optimal move")
            
            elif cmd == "analyze":
                if game.board.is_game_over():
                    print(f"Game over! Result: {game.board.result()}")
                    continue
                
                analysis = game.get_position_analysis()
                print(f"\nPosition Analysis:")
                print(f"  FEN: {analysis['fen']}")
                print(f"  Evaluation: {analysis['evaluation']:.2f} pawns")
                print(f"  Best move: {analysis['best_move']}")
                if analysis.get("pv"):
                    print(f"  Principal variation: {' → '.join(analysis['pv'][:5])}")
                if analysis.get("nodes"):
                    print(f"  Nodes searched: {analysis['nodes']:,}")
                print()
            
            elif cmd == "board":
                print("\n" + game.get_board_diagram())
                print(f"Move: {game.move_count}")
                print(f"Turn: {'White' if game.board.turn else 'Black'}")
                print()
            
            elif cmd == "legal":
                legal_moves = game.get_legal_moves()
                print(f"Legal moves ({len(legal_moves)}):")
                # Group moves for better display
                for i, move in enumerate(legal_moves):
                    print(move, end="  ")
                    if (i + 1) % 10 == 0:
                        print()
                print()
            
            elif cmd == "reset":
                game.reset()
                print("Game reset!")
                print("\n" + game.get_board_diagram())
                print()
            
            elif cmd == "save":
                filename = command[1] if len(command) > 1 else "training_data.json"
                game.export_training_data(filename)
                print(f"Saved {game.move_count} moves to {filename}")
            
            else:
                print(f"Unknown command: {cmd}. Type 'help' for commands.")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Use 'quit' to exit.")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()

