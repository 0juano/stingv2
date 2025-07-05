#!/bin/bash
# Secure deployment script with environment management

# Store your API keys here (this file stays local, never committed)
OPENROUTER_KEY="YOUR_OPENROUTER_KEY_HERE"
TAVILY_KEY="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"

echo "🚀 One-click deploy to DigitalOcean..."

# Push code (without sensitive data)
git add -A
git commit -m "Deploy updates" || true
git push origin main

# Deploy and update environment on server
ssh root@147.182.248.187 << EOF
cd /opt/proyecto-sting
git pull origin main

# Create .env with your keys
cat > .env << 'ENVFILE'
OPENROUTER_API_KEY=$OPENROUTER_KEY
TAVILY_API_KEY=$TAVILY_KEY
ENABLE_SEARCH=true
ENVFILE

# Restart everything
docker-compose down && docker-compose up -d --build
echo "✅ Deploy complete!"
EOF

echo "🌐 Your site is ready at http://147.182.248.187/"