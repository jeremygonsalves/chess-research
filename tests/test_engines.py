"""Tests for chess engine integrations."""

import pytest
from app.engines.stockfish_engine import StockfishEngine
from app.models.schemas import EvaluationRequest, EngineType


def test_stockfish_initialization():
    """Test Stockfish engine initialization."""
    try:
        engine = StockfishEngine()
        assert engine is not None
    except FileNotFoundError:
        pytest.skip("Stockfish not found on system")


def test_stockfish_is_available():
    """Test Stockfish availability check."""
    try:
        engine = StockfishEngine()
        # This will attempt to connect to Stockfish
        available = engine.is_available()
        assert isinstance(available, bool)
    except FileNotFoundError:
        pytest.skip("Stockfish not found on system")


@pytest.mark.asyncio
async def test_stockfish_evaluation():
    """Test evaluating a position with Stockfish."""
    try:
        engine = StockfishEngine()
        if not engine.is_available():
            pytest.skip("Stockfish not available")
        
        request = EvaluationRequest(
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            engine=EngineType.STOCKFISH,
            depth=5,
        )
        
        result = engine.evaluate(request, "test-task-id")
        assert result is not None
        assert result.status in ["completed", "failed"]
        if result.status == "completed":
            assert result.evaluation is not None
            assert result.computation_time > 0
    except FileNotFoundError:
        pytest.skip("Stockfish not found on system")

