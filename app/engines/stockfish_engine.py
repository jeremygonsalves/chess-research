"""Stockfish chess engine integration."""

import subprocess
import time
from datetime import datetime
from pathlib import Path

import chess
import chess.engine

from app.engines.base import BaseEngine
from app.models.schemas import EngineType, EvaluationRequest, EvaluationResult


class StockfishEngine(BaseEngine):
    """Stockfish engine wrapper."""

    def __init__(self, engine_path: str = None):
        """Initialize Stockfish engine.

        Args:
            engine_path: Path to stockfish executable. If None, tries common paths.
        """
        if engine_path is None:
            engine_path = self._find_stockfish()
        super().__init__(engine_path)

    def _find_stockfish(self) -> str:
        """Try to find stockfish in common locations.

        Returns:
            Path to stockfish executable

        Raises:
            FileNotFoundError: If stockfish cannot be found
        """
        common_paths = [
            "/usr/local/bin/stockfish",
            "/usr/bin/stockfish",
            "stockfish",  # In PATH
        ]
        for path in common_paths:
            if path == "stockfish":
                # Check if it's in PATH
                try:
                    result = subprocess.run(
                        ["which", "stockfish"], capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        return result.stdout.strip()
                except FileNotFoundError:
                    continue
            elif Path(path).exists():
                return path

        raise FileNotFoundError(
            "Stockfish not found. Please install Stockfish or specify the path."
        )

    def evaluate(
        self, request: EvaluationRequest, task_id: str
    ) -> EvaluationResult:
        """Evaluate a chess position using Stockfish.

        Args:
            request: Evaluation request
            task_id: Unique task identifier

        Returns:
            EvaluationResult with evaluation and metadata
        """
        start_time = time.time()
        created_at = datetime.utcnow()

        try:
            board = chess.Board(request.fen)

            # Configure engine limits
            limit = chess.engine.Limit(depth=request.depth)
            if request.time_limit:
                limit = chess.engine.Limit(time=request.time_limit)

            # Run evaluation
            with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
                info = engine.analyse(board, limit)
                result = info["score"].white()

                # Extract evaluation (convert to centipawns)
                evaluation_cp = result.score()
                if evaluation_cp is None:
                    # Mate found
                    mate_score = result.mate()
                    if mate_score is not None:
                        evaluation_cp = 30000 if mate_score > 0 else -30000
                    else:
                        evaluation_cp = 0

                # Get best move and principal variation
                best_move = None
                pv = []
                if "pv" in info:
                    pv_moves = info["pv"]
                    if pv_moves:
                        best_move = str(pv_moves[0])
                        pv = [str(move) for move in pv_moves[:5]]  # First 5 moves

                # Get nodes searched
                nodes = info.get("nodes", None)

                computation_time = time.time() - start_time
                completed_at = datetime.utcnow()

                return EvaluationResult(
                    task_id=task_id,
                    fen=request.fen,
                    engine=request.engine,
                    depth=request.depth,
                    evaluation=evaluation_cp / 100.0,  # Convert to pawns
                    best_move=best_move,
                    pv=pv if pv else None,
                    computation_time=computation_time,
                    nodes_searched=nodes,
                    status="completed",
                    created_at=created_at,
                    completed_at=completed_at,
                    error=None,
                )

        except Exception as e:
            computation_time = time.time() - start_time
            return EvaluationResult(
                task_id=task_id,
                fen=request.fen,
                engine=request.engine,
                depth=request.depth,
                evaluation=0.0,
                best_move=None,
                pv=None,
                computation_time=computation_time,
                nodes_searched=None,
                status="failed",
                created_at=created_at,
                completed_at=datetime.utcnow(),
                error=str(e),
            )

    def is_available(self) -> bool:
        """Check if Stockfish is available.

        Returns:
            True if Stockfish can be executed
        """
        try:
            with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
                return True
        except Exception:
            return False

    def get_info(self) -> dict:
        """Get Stockfish engine information.

        Returns:
            Dictionary with engine name and version
        """
        try:
            with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
                info = engine.id
                return {
                    "name": info.get("name", "Stockfish"),
                    "author": info.get("author", "Stockfish Team"),
                    "type": EngineType.STOCKFISH.value,
                }
        except Exception as e:
            return {
                "name": "Stockfish",
                "type": EngineType.STOCKFISH.value,
                "error": str(e),
            }

