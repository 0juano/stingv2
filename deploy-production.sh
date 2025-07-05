#!/bin/bash
# Deploy to production with proper configuration

echo "🚀 Deploying to production with dynamic URL support..."

# First, commit and push changes
echo "📦 Pushing code to GitHub..."
git add -A
git commit -m "Fix frontend dynamic URL detection for mobile/other computers" || true
git push origin main

# Deploy to remote server
ssh root@$REMOTE_HOST << 'EOF'
cd /opt/proyecto-sting

echo "📥 Pulling latest code..."
git pull origin main

echo "🔧 Ensuring proper production configuration..."
# Remove local development override if it exists
if [ -f docker-compose.override.yml ]; then
  echo "Removing local override file..."
  rm docker-compose.override.yml
fi

# Use production configuration
echo "🏗️ Building with production configuration..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build frontend

echo "🔄 Restarting services..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to start..."
sleep 10

echo "✅ Deployment complete!"
echo "🧪 Testing the API..."
curl -X POST http://localhost:8001/route \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}' | jq

echo ""
echo "🌐 Your site should now work from any device at http://147.182.248.187/"
EOF