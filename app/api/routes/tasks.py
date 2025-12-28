"""Task management endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/tasks/stats")
async def get_task_stats():
    """Get statistics about task queue and processing."""
    from app.workers.celery_app import celery_app

    inspect = celery_app.control.inspect()

    # Get active tasks
    active = inspect.active()
    scheduled = inspect.scheduled()
    reserved = inspect.reserved()

    stats = {
        "active_tasks": sum(len(tasks) for tasks in (active or {}).values()),
        "scheduled_tasks": sum(len(tasks) for tasks in (scheduled or {}).values()),
        "reserved_tasks": sum(len(tasks) for tasks in (reserved or {}).values()),
        "workers": list((active or {}).keys()),
    }

    return stats

