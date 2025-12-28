# Get Running in 5 Minutes

## Pre-flight Checklist

- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] Redis installed OR Docker installed
- [ ] Stockfish chess engine installed

## Fastest Path to Results

### 1️⃣ Install Everything (1 minute)
```bash
pip install -r requirements.txt
```

### 2️⃣ Start Redis (30 seconds)
```bash
# If you have Docker:
docker run -d -p 6379:6379 --name redis redis:7-alpine

# If you have Redis installed:
redis-server
```

### 3️⃣ Start Services (2 minutes)

**Open 3 terminals:**

**Terminal 1 - API:**
```bash
uvicorn app.api.main:app --reload --port 8000
```
Wait for: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Worker:**
```bash
celery -A app.workers.celery_app worker --loglevel=info
```
Wait for: `celery@... ready`

**Terminal 3 - Dashboard (optional but recommended):**
```bash
streamlit run app/dashboard/main.py --server.port=8501
```

### 4️⃣ See Results! (30 seconds)

**Option A: Dashboard (Easiest)**
1. Open browser: http://localhost:8501
2. Click "Submit Evaluation"
3. Click "Submit Evaluation" button
4. Go to "Task Status" tab
5. Enter your task ID and click "Check Status"
6. See results! 🎉

**Option B: Command Line**
```bash
python examples/evaluate_position.py
```

**Option C: API Docs**
1. Open browser: http://localhost:8000/docs
2. Try the `/api/v1/evaluate` endpoint
3. See the interactive API!

## 🎓 What You'll See

After submitting an evaluation, you'll get:
- **Evaluation**: Position score in pawns (positive = white advantage)
- **Best Move**: The recommended move
- **Principal Variation**: The best line of play
- **Computation Time**: How long it took
- **Nodes Searched**: How many positions Stockfish analyzed

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Redis connection refused" | Make sure Redis is running: `redis-cli ping` |
| "Stockfish not found" | Install: `brew install stockfish` (macOS) or `sudo apt-get install stockfish` (Linux) |
| "Module not found" | Run: `pip install -r requirements.txt` |
| Worker not processing | Check Redis is running and worker shows "ready" status |

## 📚 Need More Help?

- **Detailed Guide**: See [QUICKSTART.md](QUICKSTART.md)
- **Full Documentation**: See [README.md](README.md)
- **API Reference**: Visit http://localhost:8000/docs when API is running

## 🎮 Try These Test Positions

```python
# Starting position (equal)
"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# King's Gambit
"rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
```

---

**Ready? Start at step 1 above!** ⬆️

