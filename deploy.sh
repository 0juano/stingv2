#!/bin/bash

# Deploy script for production server
# Usage: ./deploy.sh

echo "🚀 Starting deployment..."

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin main

# Rebuild and restart frontend
echo "🔨 Rebuilding frontend..."
docker-compose build --no-cache frontend

# Remove old container if exists
echo "🗑️  Removing old container..."
docker rm -f frontend 2>/dev/null || true

# Start new container
echo "✨ Starting new container..."
docker-compose up -d frontend

# Check status
echo "✅ Checking container status..."
docker ps | grep frontend

echo "🎉 Deployment complete!"