#!/bin/bash
# Fix remote server with proper .env file

ssh root@147.182.248.187 << 'EOF'
cd /opt/proyecto-sting

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Create proper .env file
echo "🔑 Creating proper .env file..."
cat > .env << 'ENVFILE'
OPENROUTER_API_KEY=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
TAVILY_API_KEY=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
ENABLE_SEARCH=true
ENVFILE

# Rebuild and restart everything
echo "🔄 Rebuilding and restarting all services..."
docker-compose down
docker-compose up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Test the API
echo "🧪 Testing API..."
curl -X POST http://localhost:8001/route \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}' | jq

echo "✅ Done! Check http://147.182.248.187/"
EOF