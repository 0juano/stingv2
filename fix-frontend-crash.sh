#!/bin/bash
# Fix frontend container crash

ssh root@147.182.248.187 << 'EOF'
cd /opt/proyecto-sting

# Remove the problematic frontend container
echo "🗑️ Removing crashed frontend container..."
docker rm -f frontend

# Remove any override files
rm -f docker-compose.override.yml

# Rebuild frontend from scratch
echo "🔨 Rebuilding frontend from scratch..."
docker-compose build --no-cache frontend

# Start frontend
echo "🚀 Starting frontend..."
docker-compose up -d frontend

# Check if it's running
echo "✅ Checking container status..."
docker ps | grep frontend

echo "🌐 Frontend should be working at http://147.182.248.187/"
EOF