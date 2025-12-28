# Quick Start Guide

Follow these steps to get the Distributed Chess Engine Evaluation Platform running and see results!

## Prerequisites Check

Before starting, make sure you have:
- Python 3.10+ installed
- Redis installed and running (or we'll start it with Docker)
- Stockfish chess engine installed

### Quick Install Check

```bash
# Check Python version
python3 --version  # Should be 3.10+

# Check if Redis is installed
redis-cli --version

# Check if Stockfish is installed
stockfish --version
```

## Step 1: Install Dependencies

```bash
# Navigate to the project directory (you should already be here)
cd /path/to/chess-research

# Install Python packages
pip install -r requirements.txt
```

**Troubleshooting:** If you get permission errors, use `pip install --user -r requirements.txt`

## Step 2: Start Redis

You have two options:

### Option A: Using Redis directly (if installed)
```bash
# Start Redis server (in a new terminal)
redis-server
```

### Option B: Using Docker (recommended if Redis isn't installed)
```bash
# Start just Redis
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

## Step 3: Verify Stockfish is Available

```bash
# Try to find Stockfish
which stockfish

# If not found, install it:
# macOS:
brew install stockfish

# Ubuntu/Debian:
sudo apt-get install stockfish

# Or download from: https://stockfishchess.org/download/
```

## Step 4: Start the Services

You'll need **3 terminal windows** open:

### Terminal 1: Start the API Server
```bash
cd /path/to/chess-research
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Start the Celery Worker
```bash
cd /path/to/chess-research
celery -A app.workers.celery_app worker --loglevel=info
```

You should see:
```
celery@hostname v5.3.4 ready
```

### Terminal 3: Start the Dashboard (Optional but Recommended)
```bash
cd /path/to/chess-research
streamlit run app/dashboard/main.py --server.port=8501
```

**Or use the startup script (all in one):**
```bash
bash scripts/start.sh
```

## Step 5: Test the API

Open a **4th terminal** and test the API:

### Option A: Using the Example Script
```bash
cd /path/to/chess-research
python examples/evaluate_position.py
```

### Option B: Using curl
```bash
# Submit an evaluation task
curl -X POST "http://localhost:8000/api/v1/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "engine": "stockfish",
    "depth": 10
  }'
```

This will return a `task_id`. Copy it and check the status:

```bash
# Replace YOUR_TASK_ID with the ID from above
curl "http://localhost:8000/api/v1/evaluate/YOUR_TASK_ID"
```

### Option C: Using Python Interactive Shell
```python
import requests
import time

# Submit evaluation
response = requests.post("http://localhost:8000/api/v1/evaluate", json={
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "engine": "stockfish",
    "depth": 10
})

task_id = response.json()["task_id"]
print(f"Task ID: {task_id}")

# Check status
while True:
    status = requests.get(f"http://localhost:8000/api/v1/evaluate/{task_id}").json()
    if status["status"] == "completed":
        result = status["result"]
        print(f"Evaluation: {result['evaluation']} pawns")
        print(f"Best Move: {result.get('best_move')}")
        print(f"Time: {result['computation_time']:.3f}s")
        break
    elif status["status"] == "failed":
        print("Task failed!")
        break
    time.sleep(0.5)
    print(".", end="", flush=True)
```

## Step 6: View Results

### Option A: Use the Dashboard (Easiest!)
1. Open your browser to: **http://localhost:8501**
2. Go to "Submit Evaluation" page
3. Enter a FEN string (or use the default starting position)
4. Click "Submit Evaluation"
5. Go to "Task Status" page to see the result

### Option B: Use the API Documentation
1. Open your browser to: **http://localhost:8000/docs**
2. Try the `/api/v1/evaluate` endpoint
3. Click "Try it out"
4. Submit a position
5. Use the returned `task_id` with `/api/v1/evaluate/{task_id}` to get results

### Option C: View Metrics
Visit: **http://localhost:8000/metrics** to see Prometheus metrics

## Common Issues & Solutions

### "Redis connection refused"
- Make sure Redis is running: `redis-cli ping`
- If using Docker: `docker ps` to check if Redis container is running

### "Stockfish not found"
- Install Stockfish: `brew install stockfish` (macOS) or `sudo apt-get install stockfish` (Linux)
- Or set the path in `.env`: `STOCKFISH_PATH=/path/to/stockfish`

### "Module not found" errors
- Make sure you installed requirements: `pip install -r requirements.txt`
- Check you're in the project directory

### Celery worker not processing tasks
- Check Redis connection
- Look at worker logs for errors
- Verify worker shows "ready" status

## Example FEN Positions to Test

```bash
# Starting position (equal)
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

# King's Gambit (interesting opening)
rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1

# Ruy Lopez (popular opening)
r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4
```

## Next Steps

Once everything is working:
1. Try batch evaluations (multiple positions at once)
2. Experiment with different depths
3. Monitor the dashboard for real-time stats
4. Scale up by running multiple workers

## Stopping the Services

Press `Ctrl+C` in each terminal window to stop the services.

If you used Docker for Redis:
```bash
docker stop redis
docker rm redis
```

