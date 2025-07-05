#!/bin/bash
# Fix frontend to use dynamic environment detection

ssh root@147.182.248.187 << 'EOF'
cd /opt/proyecto-sting

# Remove any override file that might set VITE_API_BASE_URL
rm -f docker-compose.override.yml

# Check if there's an env file setting VITE variables
if grep -q "VITE_" .env 2>/dev/null; then
  echo "Removing VITE variables from .env..."
  grep -v "VITE_" .env > .env.tmp && mv .env.tmp .env
fi

# Rebuild frontend without any VITE_API_BASE_URL set
echo "🔨 Rebuilding frontend without hardcoded API URL..."
docker-compose build --no-cache frontend
docker-compose up -d frontend

echo "✅ Frontend rebuilt with dynamic environment detection!"
echo "🧪 Wait 10 seconds then check http://147.182.248.187/"
EOF