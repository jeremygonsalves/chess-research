"""Prometheus metrics for the chess evaluation platform."""

from prometheus_client import Counter, Histogram, Gauge

# Task metrics
tasks_submitted = Counter(
    "chess_evaluation_tasks_submitted_total",
    "Total number of evaluation tasks submitted",
    ["engine", "depth"],
)

tasks_completed = Counter(
    "chess_evaluation_tasks_completed_total",
    "Total number of evaluation tasks completed",
    ["engine", "status"],
)

task_duration = Histogram(
    "chess_evaluation_task_duration_seconds",
    "Time taken to evaluate a chess position",
    ["engine", "depth"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
)

evaluation_value = Histogram(
    "chess_evaluation_value_pawns",
    "Chess position evaluation in pawns",
    ["engine"],
    buckets=[-10, -5, -3, -1, -0.5, 0, 0.5, 1, 3, 5, 10],
)

nodes_searched = Histogram(
    "chess_evaluation_nodes_searched",
    "Number of nodes searched during evaluation",
    ["engine"],
    buckets=[100, 1000, 10000, 100000, 1000000, 10000000],
)

# System metrics
active_tasks = Gauge(
    "chess_evaluation_active_tasks",
    "Number of currently active evaluation tasks",
)

workers_available = Gauge(
    "chess_evaluation_workers_available",
    "Number of available Celery workers",
)

