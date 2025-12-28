# Distributed Chess Engine Evaluation Platform

A distributed system for evaluating thousands of chess positions in parallel using multiple engines (Stockfish, LCZero) with comprehensive metrics and monitoring.

## Architecture

- **API Layer**: FastAPI backend for submitting evaluation tasks
- **Task Queue**: Redis + Celery for distributed task processing
- **Workers**: Celery worker nodes running chess engines
- **Engines**: Stockfish and LCZero support
- **Metrics**: Prometheus + Grafana for monitoring
- **Dashboard**: Streamlit interface for visualization

## Project Status

🚧 In active development - building incrementally

## Quick Start

> **📘 For detailed step-by-step instructions, see [QUICKSTART.md](QUICKSTART.md)**

### Quick Setup (5 minutes)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Redis:**
   ```bash
   # Option 1: Using Docker
   docker run -d -p 6379:6379 --name redis redis:7-alpine
   
   # Option 2: Direct installation
   redis-server
   ```

3. **Install Stockfish:**
   ```bash
   # macOS
   brew install stockfish
   
   # Linux
   sudo apt-get install stockfish
   ```

4. **Start services:**
   ```bash
   # Terminal 1: API
   uvicorn app.api.main:app --reload --port 8000
   
   # Terminal 2: Worker
   celery -A app.workers.celery_app worker --loglevel=info
   
   # Terminal 3: Dashboard (optional)
   streamlit run app/dashboard/main.py --server.port=8501
   ```

5. **Test it:**
   ```bash
   python examples/evaluate_position.py
   ```

   Or visit:
   - API Docs: http://localhost:8000/docs
   - Dashboard: http://localhost:8501

### Full Installation Details

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (if not using Docker)
redis-server

# Start API server
uvicorn app.api.main:app --reload

# Start Celery worker
celery -A app.workers.celery_app worker --loglevel=info

# Start dashboard
streamlit run app/dashboard/main.py
```

### Docker Setup

```bash
docker-compose up
```

## Structure

```
chess-research/
├── app/
│   ├── api/          # FastAPI application
│   ├── workers/      # Celery workers
│   ├── engines/      # Chess engine integrations
│   ├── models/       # Data models
│   ├── metrics/      # Prometheus metrics
│   └── dashboard/    # Streamlit dashboard
├── docker/           # Docker configurations
├── k8s/              # Kubernetes manifests
└── tests/            # Test suite
```

## Features

- ✅ **Distributed Task Processing**: Redis + Celery for parallel evaluation
- ✅ **Stockfish Integration**: Full support for Stockfish engine
- ✅ **RESTful API**: FastAPI with OpenAPI documentation
- ✅ **Real-time Metrics**: Prometheus metrics endpoint
- ✅ **Web Dashboard**: Streamlit interface for monitoring
- ✅ **Docker Support**: Complete Docker Compose setup
- ✅ **Kubernetes Manifests**: Ready for K8s deployment
- 🚧 **LCZero Integration**: Coming soon
- 🚧 **Grafana Dashboards**: Coming soon

## API Endpoints

### Submit Evaluation
```bash
POST /api/v1/evaluate
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "engine": "stockfish",
  "depth": 15,
  "time_limit": 5.0  # optional
}
```

### Check Task Status
```bash
GET /api/v1/evaluate/{task_id}
```

### Batch Evaluation
```bash
POST /api/v1/evaluate/batch
{
  "positions": [
    {"fen": "...", "engine": "stockfish", "depth": 15},
    ...
  ]
}
```

### Metrics
```bash
GET /metrics  # Prometheus metrics
```

## Usage Examples

### Using the API

```python
import requests

# Submit evaluation
response = requests.post("http://localhost:8000/api/v1/evaluate", json={
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "engine": "stockfish",
    "depth": 15
})

task_id = response.json()["task_id"]

# Check status
status = requests.get(f"http://localhost:8000/api/v1/evaluate/{task_id}")
result = status.json()["result"]
print(f"Evaluation: {result['evaluation']} pawns")
```

### Using Make Commands

```bash
make install          # Install dependencies
make run-api          # Start API server
make run-worker       # Start Celery worker
make run-dashboard    # Start Streamlit dashboard
make run-all          # Start all services
make docker-up        # Start with Docker Compose
make test             # Run tests
```

## Metrics

The platform exposes Prometheus metrics at `/metrics`:

- `chess_evaluation_tasks_submitted_total`: Total tasks submitted
- `chess_evaluation_tasks_completed_total`: Total tasks completed
- `chess_evaluation_task_duration_seconds`: Task execution time
- `chess_evaluation_value_pawns`: Position evaluation values
- `chess_evaluation_nodes_searched`: Nodes searched by engines

## Development

### Project Structure

```
chess-research/
├── app/
│   ├── api/              # FastAPI application
│   │   ├── routes/       # API endpoints
│   │   └── main.py       # FastAPI app
│   ├── workers/          # Celery workers
│   │   ├── celery_app.py # Celery configuration
│   │   └── tasks.py      # Task definitions
│   ├── engines/          # Chess engine integrations
│   │   ├── base.py       # Base engine interface
│   │   └── stockfish_engine.py
│   ├── models/           # Pydantic models
│   ├── metrics/          # Prometheus metrics
│   ├── dashboard/        # Streamlit dashboard
│   └── config.py         # Configuration
├── docker/               # Dockerfiles
├── k8s/                  # Kubernetes manifests
├── scripts/              # Utility scripts
└── tests/                # Test suite
```

## Next Steps

1. **LCZero Integration**: Add LCZero neural network engine support
2. **Grafana Dashboards**: Create visualization dashboards
3. **Performance Optimization**: Benchmark and optimize worker performance
4. **Cost Analysis**: Track compute costs per evaluation
5. **Load Testing**: Stress test the system with thousands of positions

## Research Framing

This project demonstrates:
- **Distributed Systems**: Scalable task queue architecture
- **ML Systems Benchmarking**: Chess as a controlled workload
- **Performance Engineering**: Metrics-driven optimization
- **Infrastructure-first Research**: Production-ready deployment


