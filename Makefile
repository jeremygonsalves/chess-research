.PHONY: install run-api run-worker run-dashboard run-all docker-up docker-down test clean

install:
	pip install -r requirements.txt

run-api:
	uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	celery -A app.workers.celery_app worker --loglevel=info

run-dashboard:
	streamlit run app/dashboard/main.py --server.port=8501

run-all:
	@echo "Starting all services..."
	@bash scripts/start.sh

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

test:
	pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete

