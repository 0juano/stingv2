#!/bin/bash
cd /app

# Start all services in background
echo "Starting router service..."
cd agents/router && uvicorn main:app --host 0.0.0.0 --port 8001 &

echo "Starting BCRA service..."
cd /app/agents/bcra && uvicorn main:app --host 0.0.0.0 --port 8002 &

echo "Starting Comex service..."
cd /app/agents/comex && uvicorn main:app --host 0.0.0.0 --port 8003 &

echo "Starting Senasa service..."
cd /app/agents/senasa && uvicorn main:app --host 0.0.0.0 --port 8004 &

echo "Starting Auditor service..."
cd /app/agents/auditor && uvicorn main:app --host 0.0.0.0 --port 8005 &

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Start proxy on Railway PORT
echo "Starting proxy server on port ${PORT:-8000}..."
cd /app && python proxy.py