"""Base class for chess engine integrations."""

from abc import ABC, abstractmethod
from typing import Optional

from app.models.schemas import EvaluationRequest, EvaluationResult


class BaseEngine(ABC):
    """Abstract base class for chess engines."""

    def __init__(self, engine_path: str):
        """Initialize the engine.

        Args:
            engine_path: Path to the engine executable
        """
        self.engine_path = engine_path
        self._engine = None

    @abstractmethod
    def evaluate(
        self, request: EvaluationRequest, task_id: str
    ) -> EvaluationResult:
        """Evaluate a chess position.

        Args:
            request: Evaluation request with position and parameters
            task_id: Unique task identifier

        Returns:
            EvaluationResult with the evaluation and metadata
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the engine is available and can be used.

        Returns:
            True if engine is available, False otherwise
        """
        pass

    @abstractmethod
    def get_info(self) -> dict:
        """Get information about the engine.

        Returns:
            Dictionary with engine information (name, version, etc.)
        """
        pass

