.PHONY: help dev build up down logs test clean frontend-dev

# Default target
help:
	@echo "Bureaucracy Oracle - Development Commands"
	@echo "========================================"
	@echo "make dev        - Start all services with hot reload"
	@echo "make build      - Build all Docker images"
	@echo "make up         - Start all services"
	@echo "make down       - Stop all services"
	@echo "make logs       - Show logs from all services"
	@echo "make test       - Run test query"
	@echo "make clean      - Clean up containers and images"
	@echo "make frontend   - Start frontend development server"

# Development mode with hot reload
dev:
	docker-compose up --build

# Build all images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Test with a sample query
test:
	@echo "Testing with sample query..."
	python3 orchestrator.py "¿Cómo hago para exportar aceitunas a Grecia?"

# Test individual services
test-router:
	curl -X POST http://localhost:8001/route \
		-H "Content-Type: application/json" \
		-d '{"question": "¿Cómo exportar aceitunas?"}'

test-comex:
	curl -X POST http://localhost:8003/answer \
		-H "Content-Type: application/json" \
		-d '{"question": "¿Cómo exportar aceitunas a Grecia?"}'

test-bcra:
	curl -X POST http://localhost:8002/answer \
		-H "Content-Type: application/json" \
		-d '{"question": "¿Cómo pagar Netflix desde Argentina?"}'

test-health:
	@echo "Checking service health..."
	@curl -s http://localhost:8001/health | jq '.'
	@curl -s http://localhost:8002/health | jq '.'
	@curl -s http://localhost:8003/health | jq '.'
	@curl -s http://localhost:8004/health | jq '.'
	@curl -s http://localhost:8005/health | jq '.'

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Frontend development (when implemented)
frontend:
	cd frontend && npm install && npm run dev

# Install Python dependencies for local testing
install-deps:
	pip install httpx pydantic fastapi uvicorn pyyaml

# Format code
format:
	find . -name "*.py" -type f -exec black {} \;

# Quick restart of a specific service
restart-%:
	docker-compose restart $*

# View specific service logs
logs-%:
	docker-compose logs -f $*

# Environment setup
setup:
	@test -f .env || cp .env.example .env
	@echo "✅ Environment file created. Please edit .env with your OpenRouter API key."
	@echo "📦 Installing Python dependencies..."
	@pip install httpx
	@echo "🚀 Ready to run 'make dev'"