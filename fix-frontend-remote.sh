#!/bin/bash
# Fix frontend to use correct API URLs on remote server

ssh root@147.182.248.187 << 'EOF'
cd /opt/proyecto-sting

# Update docker-compose to pass correct API URL to frontend build
cat > docker-compose.override.yml << 'OVERRIDE'
version: '3.8'

services:
  frontend:
    build:
      args:
        VITE_API_BASE_URL: http://147.182.248.187:8001
OVERRIDE

# Rebuild only the frontend with correct API URL
echo "🔨 Rebuilding frontend with correct API URL..."
docker-compose up -d --build frontend

echo "✅ Frontend rebuilt! Testing..."
sleep 5

# Test the API
curl -X POST http://localhost:8001/route \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuál es el límite para pagos al exterior?"}' | jq

echo "🌐 Site should now work at http://147.182.248.187/"
EOF