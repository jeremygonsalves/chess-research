"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}


@router.get("/health/engines")
async def engines_health():
    """Check status of chess engines."""
    from app.engines import StockfishEngine
    from app.config import settings

    engines_status = {}

    # Check Stockfish
    try:
        stockfish = StockfishEngine(settings.STOCKFISH_PATH)
        engines_status["stockfish"] = {
            "available": stockfish.is_available(),
            "info": stockfish.get_info(),
        }
    except Exception as e:
        engines_status["stockfish"] = {
            "available": False,
            "error": str(e),
        }

    return {"engines": engines_status}

