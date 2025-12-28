# Interactive Chess Game with Optimal Moves

A simple chess game that shows the optimal move at every step, designed for collecting training data to build an ML model that predicts optimal moves with 100% accuracy.

## Quick Start

### Option 1: Interactive Command-Line Game

```bash
python -m app.game.interactive_game
```

Commands:
- `move e2e4` - Make a move
- `best` - Show optimal move
- `analyze` - Detailed position analysis
- `board` - Show board
- `legal` - Show legal moves
- `save training.json` - Export training data
- `reset` - Start new game
- `quit` - Exit

### Option 2: Streamlit Web Interface

```bash
streamlit run app/game/game_streamlit.py
```

Then open http://localhost:8501 in your browser.

### Option 3: Generate Training Data Automatically

```bash
# Generate 10 games automatically
python scripts/generate_training_data.py 10

# Generate 100 games with deeper analysis
python scripts/generate_training_data.py 100 20
```

## ML Model Training

### Step 1: Collect Training Data

Play games or generate automatically:

```bash
python scripts/generate_training_data.py 50
```

This creates `chess_training_data_50games.json` with positions and optimal moves.

### Step 2: Train the Model

```bash
# Install scikit-learn if needed
pip install scikit-learn

# Train model
python app/ml/train_model.py chess_training_data_50games.json
```

The model will:
- Extract features from chess positions (FEN strings)
- Learn to predict optimal moves
- Save to `chess_move_predictor.pkl`

### Step 3: Improve the Model

Current implementation uses:
- Simple feature extraction (piece positions, material, etc.)
- Random Forest classifier

**To reach 100% accuracy, consider:**
1. Better feature engineering:
   - Piece-square tables
   - Attack/defense maps
   - Piece mobility
   - King safety
   - Pawn structure

2. Advanced models:
   - Neural networks (CNN for board representation)
   - Transformer models
   - Reinforcement learning

3. More training data:
   - Generate thousands of games
   - Include positions from real games
   - Balance training data (various positions)

## Data Format

Training data is saved as JSON:

```json
{
  "game_number": 1,
  "total_moves": 45,
  "moves": [
    {
      "move_number": 1,
      "move_played": "e2e4",
      "fen_before": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
      "fen_after": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
      "optimal_move": "e7e5",
      "evaluation": 0.15,
      "timestamp": "2025-01-01T12:00:00"
    }
  ]
}
```

## Project Goal

Build an ML model that can predict the optimal chess move for any position with **100% accuracy**.

This is a challenging goal because:
- Chess has ~10^43 possible positions
- Optimal moves depend on deep strategic understanding
- Some positions have multiple equally good moves

**Strategy:**
1. Collect as much training data as possible
2. Use Stockfish (depth 15+) to ensure "optimal" moves
3. Iteratively improve features and models
4. Test accuracy on held-out positions

## Next Steps

1. **Generate more data**: Run `generate_training_data.py` with 1000+ games
2. **Improve features**: Enhance `fen_to_features()` with better chess knowledge
3. **Try neural networks**: Use TensorFlow/PyTorch for deeper models
4. **Evaluate on test set**: Measure accuracy on unseen positions
5. **Iterate**: Keep improving until you reach 100% accuracy!

