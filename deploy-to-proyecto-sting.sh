#!/bin/bash
# Deploy to Railway "Proyecto-Sting"

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚂 Deploying to Railway - Proyecto-Sting${NC}"

# Link to the project
echo -e "\n${YELLOW}Linking to Proyecto-Sting...${NC}"
echo "Please select: 0juano's Projects → Proyecto-Sting"
railway link

# Set environment variables
echo -e "\n${YELLOW}Setting environment variables...${NC}"
echo "Setting OPENROUTER_API_KEY..."
railway variables set OPENROUTER_API_KEY="${OPENROUTER_API_KEY}"

echo "Setting TAVILY_API_KEY..."
railway variables set TAVILY_API_KEY="${TAVILY_API_KEY}"

echo "Setting ENABLE_SEARCH..."
railway variables set ENABLE_SEARCH="true"

# Deploy
echo -e "\n${YELLOW}Deploying application...${NC}"
railway up

echo -e "\n${GREEN}✅ Deployment initiated!${NC}"
echo ""
echo "Check deployment status with:"
echo "  railway logs"
echo ""
echo "Once deployed, your app will be available at:"
echo "  https://proyecto-sting.up.railway.app"