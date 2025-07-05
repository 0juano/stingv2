#!/bin/bash
# Deploy to production with EXPLICIT build args to fix frontend URLs

echo "🚀 Deploying to production with correct API URLs..."

# Push code to GitHub (without .env!)
echo "📦 Pushing code to GitHub..."
git add frontend/src/hooks/useOrchestrator.ts
git add docker-compose.yml docker-compose.prod.yml
git add frontend/Dockerfile
git commit -m "Fix production frontend to use server IPs" || true
git push origin main

# Deploy to remote server
ssh root@147.182.248.187 << 'EOF'
cd /opt/proyecto-sting

echo "📥 Pulling latest code..."
git pull origin main

echo "🔧 Building frontend with EXPLICIT production URLs..."
# Remove any existing frontend container and image
docker rm -f frontend 2>/dev/null || true
docker rmi proyecto-sting_frontend 2>/dev/null || true

# Build with explicit args to ensure they're used
docker build \
  --build-arg VITE_API_BASE_URL=http://147.182.248.187:8001 \
  --build-arg VITE_BCRA_URL=http://147.182.248.187:8002 \
  --build-arg VITE_COMEX_URL=http://147.182.248.187:8003 \
  --build-arg VITE_SENASA_URL=http://147.182.248.187:8004 \
  --build-arg VITE_AUDITOR_URL=http://147.182.248.187:8005 \
  -t proyecto-sting_frontend \
  ./frontend

echo "🔄 Starting all services..."
docker-compose up -d

echo "⏳ Waiting for services..."
sleep 10

echo "✅ Deployment complete!"
echo "🧪 Testing API..."
curl -s -X POST http://localhost:8001/route \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}' | jq .decision.primary_agent

echo ""
echo "🌐 Your site should now work from ANY device at http://147.182.248.187/"
EOF