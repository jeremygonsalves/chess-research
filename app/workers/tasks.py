"""Celery tasks for chess evaluation."""

from datetime import datetime

from app.engines import StockfishEngine
from app.metrics.prometheus import (
    evaluation_value,
    nodes_searched,
    task_duration,
    tasks_completed,
)
from app.models.schemas import EngineType
from app.workers.celery_app import celery_app
from app.config import settings


@celery_app.task(bind=True, name="evaluate_position")
def evaluate_position_task(
    self, fen: str, engine: str, depth: int, time_limit: float | None
):
    """Evaluate a chess position using the specified engine.

    Args:
        fen: FEN string of the position
        engine: Engine type ("stockfish" or "lczero")
        depth: Search depth
        time_limit: Time limit in seconds (optional)

    Returns:
        Dictionary with evaluation result (matches EvaluationResult schema)
    """
    task_id = self.request.id  # Get Celery's task ID
    
    # Update task state to processing
    self.update_state(state="PROGRESS", meta={"progress": 0})

    try:
        # Select engine
        if engine == EngineType.STOCKFISH.value:
            engine_instance = StockfishEngine(settings.STOCKFISH_PATH)
        elif engine == EngineType.LCZERO.value:
            # TODO: Implement LCZero
            raise NotImplementedError("LCZero engine not yet implemented")
        else:
            raise ValueError(f"Unknown engine: {engine}")

        # Create evaluation request
        from app.models.schemas import EvaluationRequest

        request = EvaluationRequest(
            fen=fen,
            engine=EngineType(engine),
            depth=depth,
            time_limit=time_limit,
        )

        # Update progress
        self.update_state(state="PROGRESS", meta={"progress": 50})

        # Evaluate position
        result = engine_instance.evaluate(request, task_id)

        # Update progress
        self.update_state(state="PROGRESS", meta={"progress": 100})

        # Record metrics
        task_duration.labels(engine=engine, depth=depth).observe(result.computation_time)
        evaluation_value.labels(engine=engine).observe(result.evaluation)
        if result.nodes_searched:
            nodes_searched.labels(engine=engine).observe(result.nodes_searched)
        tasks_completed.labels(engine=engine, status="success").inc()

        # Convert result to dict for serialization
        result_dict = result.model_dump()
        result_dict["created_at"] = result.created_at.isoformat()
        if result.completed_at:
            result_dict["completed_at"] = result.completed_at.isoformat()

        return result_dict

    except Exception as e:
        # Record failure metrics
        tasks_completed.labels(engine=engine, status="failed").inc()
        
        # Return error result
        error_result = {
            "task_id": task_id,
            "fen": fen,
            "engine": engine,
            "depth": depth,
            "evaluation": 0.0,
            "best_move": None,
            "pv": None,
            "computation_time": 0.0,
            "nodes_searched": None,
            "status": "failed",
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "error": str(e),
        }
        return error_result

