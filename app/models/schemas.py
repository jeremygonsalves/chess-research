"""Pydantic schemas for request/response models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EngineType(str, Enum):
    """Supported chess engines."""

    STOCKFISH = "stockfish"
    LCZERO = "lczero"


class EvaluationRequest(BaseModel):
    """Request to evaluate a chess position."""

    fen: str = Field(..., description="FEN string of the position to evaluate")
    engine: EngineType = Field(default=EngineType.STOCKFISH, description="Engine to use")
    depth: int = Field(default=15, ge=1, le=30, description="Search depth")
    time_limit: Optional[float] = Field(
        default=None, ge=0.1, description="Time limit in seconds (optional)"
    )


class EvaluationResult(BaseModel):
    """Result of a chess position evaluation."""

    task_id: str
    fen: str
    engine: EngineType
    depth: int
    evaluation: float = Field(..., description="Centipawn evaluation (positive = white advantage)")
    best_move: Optional[str] = Field(None, description="Best move in UCI format")
    pv: Optional[list[str]] = Field(None, description="Principal variation (line of best moves)")
    computation_time: float = Field(..., description="Time taken in seconds")
    nodes_searched: Optional[int] = Field(None, description="Number of nodes searched")
    status: str = Field(..., description="Task status: pending, processing, completed, failed")
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class BatchEvaluationRequest(BaseModel):
    """Request to evaluate multiple chess positions."""

    positions: list[EvaluationRequest]
    priority: int = Field(default=5, ge=1, le=10, description="Task priority (1=highest, 10=lowest)")


class TaskStatus(BaseModel):
    """Status of an evaluation task."""

    task_id: str
    status: str
    progress: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    result: Optional[EvaluationResult] = None

