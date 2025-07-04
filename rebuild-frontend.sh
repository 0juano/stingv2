#!/bin/bash

# Rebuild Frontend with Correct Environment Variables
# This script ensures the frontend is built with the proper server IP addresses

echo "🔨 Rebuilding frontend container with server IP configuration..."

# Stop and remove the old frontend container
echo "📦 Stopping frontend container..."
docker-compose stop frontend
docker-compose rm -f frontend

# Remove the old frontend image to ensure a fresh build
echo "🗑️  Removing old frontend image..."
docker rmi stingv2_frontend || true

# Rebuild with no cache to ensure fresh build
echo "🏗️  Building frontend with server IPs..."
docker-compose build --no-cache frontend

# Start the updated frontend
echo "🚀 Starting frontend..."
docker-compose up -d frontend

# Wait for container to be healthy
echo "⏳ Waiting for frontend to be ready..."
sleep 5

# Check if frontend is running
if docker ps | grep -q frontend; then
    echo "✅ Frontend rebuilt successfully!"
    echo "📱 Mobile devices can now access: http://147.182.248.187"
    echo ""
    echo "🔍 To verify the build, check the logs:"
    echo "   docker-compose logs frontend"
else
    echo "❌ Frontend failed to start. Check logs with:"
    echo "   docker-compose logs frontend"
    exit 1
fi