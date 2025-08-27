.PHONY: install start backend frontend docker-build docker-up clean test

# Development commands
install:
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt

start:
	./scripts/start.sh

backend:
	.venv/bin/uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

frontend:
	.venv/bin/streamlit run frontend/streamlit_app.py --server.port 8501

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Utility commands
clean:
	rm -rf .venv/
	rm -rf __pycache__/
	rm -rf backend/__pycache__/
	rm -rf data/
	docker-compose down --volumes --remove-orphans

test:
	.venv/bin/pytest tests/ -v

format:
	.venv/bin/black backend/ frontend/
	.venv/bin/isort backend/ frontend/

lint:
	.venv/bin/flake8 backend/ frontend/

# Production commands
prod-install:
	pip install -r requirements.txt --no-dev

prod-start:
	uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4