#!/usr/bin/env bash
# Deploy individual services to Railway
# This script creates and deploys each microservice separately

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚂 Railway Multi-Service Deployment${NC}"
echo "This will create and deploy 6 services to Railway"
echo ""

# Check if logged in to Railway
if ! railway whoami >/dev/null 2>&1; then
    echo -e "${YELLOW}Please log in to Railway first${NC}"
    railway login
fi

# Get or create project
echo -e "\n${YELLOW}Setting up Railway project...${NC}"
if [ -f ".railway/config.json" ]; then
    echo -e "${GREEN}✓ Using existing Railway project${NC}"
else
    echo "Creating new Railway project..."
    railway init --name "bureaucracy-oracle"
fi

# Service configuration
declare -a SERVICES=("router" "bcra" "comex" "senasa" "auditor")
declare -A PORTS=(
    ["router"]="8001"
    ["bcra"]="8002"
    ["comex"]="8003"
    ["senasa"]="8004"
    ["auditor"]="8005"
)

# Create railway.json for each service
echo -e "\n${YELLOW}Creating service configurations...${NC}"
for service in "${SERVICES[@]}"; do
    port="${PORTS[$service]}"
    
    cat > "agents/$service/railway.json" <<EOF
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "./Dockerfile"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
EOF
    echo -e "${GREEN}✓ Created config for $service${NC}"
done

# Deploy each service
echo -e "\n${YELLOW}Deploying services to Railway...${NC}"
for service in "${SERVICES[@]}"; do
    echo -e "\n${BLUE}Deploying $service...${NC}"
    
    cd "agents/$service"
    
    # Create the service if it doesn't exist
    if ! railway status --service "$service" >/dev/null 2>&1; then
        echo "Creating service: $service"
        railway service create --name "$service"
    fi
    
    # Link to the service
    railway link --service "$service"
    
    # Set environment variables
    railway variables set OPENROUTER_API_KEY="$OPENROUTER_API_KEY" --service "$service"
    railway variables set AGENT_NAME="$service" --service "$service"
    railway variables set PORT="${PORTS[$service]}" --service "$service"
    
    # For router, set additional service URLs
    if [ "$service" = "router" ]; then
        railway variables set BCRA_SERVICE_URL="http://bcra.railway.internal:8002" --service "$service"
        railway variables set COMEX_SERVICE_URL="http://comex.railway.internal:8003" --service "$service"
        railway variables set SENASA_SERVICE_URL="http://senasa.railway.internal:8004" --service "$service"
        railway variables set AUDITOR_SERVICE_URL="http://auditor.railway.internal:8005" --service "$service"
    fi
    
    # Deploy
    echo "Deploying $service..."
    railway up --service "$service" --detach
    
    cd ../..
    echo -e "${GREEN}✓ Deployed $service${NC}"
done

# Deploy frontend separately (if exists)
if [ -d "frontend" ]; then
    echo -e "\n${BLUE}Deploying frontend...${NC}"
    cd frontend
    
    # Create frontend railway.json
    cat > railway.json <<EOF
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "./Dockerfile.prod"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
EOF
    
    # Create frontend service
    if ! railway status --service "frontend" >/dev/null 2>&1; then
        railway service create --name "frontend"
    fi
    
    railway link --service "frontend"
    railway variables set VITE_API_BASE_URL="https://router.up.railway.app" --service "frontend"
    railway variables set VITE_AUDITOR_URL="https://auditor.up.railway.app" --service "frontend"
    
    railway up --service "frontend" --detach
    cd ..
    echo -e "${GREEN}✓ Deployed frontend${NC}"
fi

# Summary
echo -e "\n${GREEN}✅ Deployment Complete!${NC}"
echo -e "\nServices deployed:"
for service in "${SERVICES[@]}"; do
    echo -e "  • $service"
done
echo -e "  • frontend (if available)"

echo -e "\n${YELLOW}Getting service URLs...${NC}"
railway status

echo -e "\n${BLUE}Next steps:${NC}"
echo "1. Check Railway dashboard for service status"
echo "2. Add custom domains if needed"
echo "3. Run health checks: ./scripts/health-check-all.sh"
echo ""
echo -e "${GREEN}🎉 Your Bureaucracy Oracle is deploying!${NC}"