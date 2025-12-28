"""Train ML model to predict optimal chess moves."""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
from typing import List, Dict
import chess
from chess import Board

# Try importing ML libraries (will install if needed)
try:
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, classification_report
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  scikit-learn not installed. Install with: pip install scikit-learn")


def fen_to_features(fen: str) -> np.ndarray:
    """Convert FEN position to feature vector.
    
    This is a simple feature extraction - you can improve this significantly!
    
    Args:
        fen: FEN string of chess position
        
    Returns:
        Feature vector (1D numpy array)
    """
    board = Board(fen)
    features = []
    
    # Piece positions (64 squares * 13 piece types = 832 features)
    piece_types = [chess.PAWN, chess.ROOK, chess.KNIGHT, chess.BISHOP, chess.QUEEN, chess.KING]
    colors = [chess.WHITE, chess.BLACK]
    
    for color in colors:
        for piece_type in piece_types:
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece and piece.piece_type == piece_type and piece.color == color:
                    features.append(1.0)
                else:
                    features.append(0.0)
    
    # Additional features
    features.append(1.0 if board.turn == chess.WHITE else 0.0)  # Turn
    features.append(1.0 if board.has_kingside_castling_rights(chess.WHITE) else 0.0)
    features.append(1.0 if board.has_queenside_castling_rights(chess.WHITE) else 0.0)
    features.append(1.0 if board.has_kingside_castling_rights(chess.BLACK) else 0.0)
    features.append(1.0 if board.has_queenside_castling_rights(chess.BLACK) else 0.0)
    
    # Material count
    for color in colors:
        for piece_type in piece_types:
            features.append(len(board.pieces(piece_type, color)))
    
    # Check status
    features.append(1.0 if board.is_check() else 0.0)
    features.append(1.0 if board.is_checkmate() else 0.0)
    features.append(1.0 if board.is_stalemate() else 0.0)
    
    return np.array(features)


def move_to_index(move_uci: str) -> int:
    """Convert UCI move to index (simplified - maps to all possible moves).
    
    Args:
        move_uci: Move in UCI format
        
    Returns:
        Move index (0-4671 for all possible chess moves)
    """
    try:
        move = chess.Move.from_uci(move_uci)
        # Map to index: from_square * 64 + to_square
        return move.from_square * 64 + move.to_square
    except:
        return 0


def load_training_data(data_file: str) -> tuple:
    """Load training data from JSON file.
    
    Args:
        data_file: Path to training data JSON file
        
    Returns:
        Tuple of (features, labels, move_strings)
    """
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    X = []
    y = []
    move_strings = []
    
    if "games" in data:
        # Multi-game format
        for game in data["games"]:
            for move_data in game["moves"]:
                if "fen_before" in move_data and "optimal_move" in move_data:
                    features = fen_to_features(move_data["fen_before"])
                    X.append(features)
                    y.append(move_to_index(move_data["optimal_move"]))
                    move_strings.append(move_data["optimal_move"])
    else:
        # Single game format
        for move_data in data["game_history"]:
            if "fen_before" in move_data and "optimal_move" in move_data:
                features = fen_to_features(move_data["fen_before"])
                X.append(features)
                y.append(move_to_index(move_data["optimal_move"]))
                move_strings.append(move_data["optimal_move"])
    
    return np.array(X), np.array(y), move_strings


def train_model(X, y, test_size=0.2):
    """Train ML model on chess position data.
    
    Args:
        X: Feature vectors
        y: Move labels (indices)
        test_size: Fraction of data for testing
        
    Returns:
        Trained model
    """
    if not ML_AVAILABLE:
        raise ImportError("scikit-learn not installed. Install with: pip install scikit-learn")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Features per sample: {X_train.shape[1]}")
    print(f"Unique moves: {len(np.unique(y))}")
    
    # Train Random Forest (start simple, can upgrade to neural networks)
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\nEvaluating model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{'='*60}")
    print(f"Model Accuracy: {accuracy:.2%}")
    print(f"{'='*60}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    return model, X_test, y_test, y_pred


def save_model(model, filename: str = "chess_move_predictor.pkl"):
    """Save trained model to file."""
    if not ML_AVAILABLE:
        raise ImportError("scikit-learn not installed")
    
    joblib.dump(model, filename)
    print(f"\n✅ Model saved to {filename}")


if __name__ == "__main__":
    import sys
    
    if not ML_AVAILABLE:
        print("Installing scikit-learn...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn"])
        print("Please run the script again.")
        sys.exit(0)
    
    # Load data
    data_file = sys.argv[1] if len(sys.argv) > 1 else "chess_training_data_10games.json"
    
    if not Path(data_file).exists():
        print(f"❌ Training data file not found: {data_file}")
        print("Generate training data first:")
        print("  python scripts/generate_training_data.py 10")
        sys.exit(1)
    
    print(f"Loading training data from {data_file}...")
    X, y, moves = load_training_data(data_file)
    
    print(f"Loaded {len(X)} training examples")
    print(f"Feature vector size: {X.shape[1]}")
    
    # Train model
    model, X_test, y_test, y_pred = train_model(X, y)
    
    # Save model
    save_model(model)

