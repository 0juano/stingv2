#!/bin/bash

# Quick deploy command for production
# Usage: ./quick-deploy.sh

echo "🚀 Deploying to production server..."

ssh root@147.182.248.187 << 'EOF'
cd /opt/proyecto-sting
echo "📥 Pulling latest changes..."
git pull origin main
echo "🔨 Rebuilding frontend..."
docker-compose build --no-cache frontend
echo "🔄 Restarting frontend..."
docker rm -f frontend 2>/dev/null || true
docker-compose up -d frontend
echo "✅ Deployment complete!"
echo "🌐 Check the site at http://147.182.248.187"
EOF