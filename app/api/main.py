"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.api.routes import evaluations, health, tasks

app = FastAPI(
    title="Distributed Chess Engine Evaluation Platform",
    description="A distributed system for evaluating chess positions using multiple engines",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(evaluations.router, prefix="/api/v1", tags=["evaluations"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Distributed Chess Engine Evaluation Platform",
        "version": "0.1.0",
        "docs": "/docs",
    }

