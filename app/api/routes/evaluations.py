"""Evaluation endpoints."""

from fastapi import APIRouter

from app.models.schemas import (
    BatchEvaluationRequest,
    EvaluationRequest,
    EvaluationResult,
    TaskStatus,
)
from app.workers.tasks import evaluate_position_task

router = APIRouter()


@router.post("/evaluate", response_model=TaskStatus)
async def evaluate_position(request: EvaluationRequest):
    """Submit a single position for evaluation.

    Returns immediately with a task ID for checking status.
    """
    # Submit task to Celery (it will generate its own task ID)
    task = evaluate_position_task.delay(
        fen=request.fen,
        engine=request.engine.value,
        depth=request.depth,
        time_limit=request.time_limit,
    )

    # Use Celery's task ID
    task_id = task.id

    # Record metrics
    from app.metrics.prometheus import tasks_submitted
    tasks_submitted.labels(engine=request.engine.value, depth=request.depth).inc()

    return TaskStatus(
        task_id=task_id,
        status="pending",
        progress=None,
        result=None,
    )


@router.post("/evaluate/batch", response_model=list[TaskStatus])
async def evaluate_batch(request: BatchEvaluationRequest):
    """Submit multiple positions for evaluation.

    Returns a list of task IDs.
    """
    task_statuses = []
    from app.metrics.prometheus import tasks_submitted

    for pos_request in request.positions:
        # Submit task to Celery
        task = evaluate_position_task.delay(
            fen=pos_request.fen,
            engine=pos_request.engine.value,
            depth=pos_request.depth,
            time_limit=pos_request.time_limit,
        )

        task_id = task.id

        # Record metrics
        tasks_submitted.labels(engine=pos_request.engine.value, depth=pos_request.depth).inc()

        task_statuses.append(
            TaskStatus(
                task_id=task_id,
                status="pending",
                progress=None,
                result=None,
            )
        )

    return task_statuses


@router.get("/evaluate/{task_id}", response_model=TaskStatus)
async def get_evaluation_status(task_id: str):
    """Get the status and result of an evaluation task."""
    from app.workers.celery_app import celery_app

    task = celery_app.AsyncResult(task_id)

    if task.state == "PENDING":
        return TaskStatus(
            task_id=task_id,
            status="pending",
            progress=None,
            result=None,
        )
    elif task.state == "PROGRESS":
        return TaskStatus(
            task_id=task_id,
            status="processing",
            progress=task.info.get("progress", 0),
            result=None,
        )
    elif task.state == "SUCCESS":
        result_data = task.result
        return TaskStatus(
            task_id=task_id,
            status="completed",
            progress=100,
            result=EvaluationResult(**result_data) if result_data else None,
        )
    else:
        # FAILURE or other error state
        error_message = str(task.info) if isinstance(task.info, Exception) else "Unknown error"
        return TaskStatus(
            task_id=task_id,
            status="failed",
            progress=None,
            result=None,
        )

