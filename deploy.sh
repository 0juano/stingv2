#!/bin/bash
# Quick deploy script for updating remote server

echo "🚀 Deploying to DigitalOcean..."

# First, commit and push any local changes
echo "📦 Pushing latest code to GitHub..."
git add -A
git commit -m "Update API key and deployment fixes" || true
git push origin main

# Create remote update script
cat > remote-update.sh << 'EOF'
#!/bin/bash
cd /opt/proyecto-sting
echo "📥 Pulling latest code..."
git pull origin main

echo "🔑 Updating API key..."
cat > .env << 'ENVFILE'
# OpenRouter API Configuration
OPENROUTER_API_KEY=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

# Tavily Search API Configuration
TAVILY_API_KEY=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

# Feature Flags
ENABLE_SEARCH=true
ENVFILE

echo "🔄 Restarting services..."
docker-compose down
docker-compose up -d --build

echo "✅ Deployment complete!"
docker ps
EOF

# Execute on remote server
echo "🖥️  Updating remote server..."
ssh root@147.182.248.187 'bash -s' < remote-update.sh

# Cleanup
rm remote-update.sh

echo "✨ Done! Your site should be working at http://147.182.248.187/"
echo "🧪 Testing the remote API..."
curl -X POST http://147.182.248.187:8001/route \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}' | jq || echo "❌ API test failed"