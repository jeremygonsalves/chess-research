#!/bin/bash
# Startup script for local development

echo "Starting Distributed Chess Engine Evaluation Platform..."

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis is not running. Starting Redis..."
    echo "Please start Redis manually: redis-server"
    exit 1
fi

echo "✅ Redis is running"

# Start API server in background
echo "Starting API server..."
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000 --reload-exclude 'venv/*' --reload-exclude '*.pyc' > api.log 2>&1 &
API_PID=$!
echo "API server started (PID: $API_PID)"

# Wait a moment for API to start
sleep 2

# Start Celery worker
echo "Starting Celery worker..."
celery -A app.workers.celery_app worker --loglevel=info > worker.log 2>&1 &
WORKER_PID=$!
echo "Celery worker started (PID: $WORKER_PID)"

# Start Dashboard
echo "Starting Streamlit dashboard..."
streamlit run app/dashboard/main.py --server.port=8501 > dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "Dashboard started (PID: $DASHBOARD_PID)"

echo ""
echo "✅ All services started!"
echo ""
echo "📊 API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "📈 Dashboard: http://localhost:8501"
echo ""
echo "Logs:"
echo "  - API: tail -f api.log"
echo "  - Worker: tail -f worker.log"
echo "  - Dashboard: tail -f dashboard.log"
echo ""
echo "To stop all services: kill $API_PID $WORKER_PID $DASHBOARD_PID"

