#!/usr/bin/env bash
# Railway deployment script for Bureaucracy Oracle
# Deploys 6 services: router, bcra, comex, senasa, auditor, frontend

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Error: Railway CLI not found${NC}"
    echo "Install with: npm install -g @railway/cli"
    exit 1
fi

# Check for project ID
PROJECT_ID="${RAILWAY_PROJECT_ID:-$1}"
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: Railway project ID required${NC}"
    echo "Usage: ./railway.sh <project-id>"
    echo "Or set RAILWAY_PROJECT_ID environment variable"
    exit 1
fi

echo -e "${YELLOW}🚀 Deploying Bureaucracy Oracle to Railway${NC}"
echo "Project ID: $PROJECT_ID"

# Link to Railway project
echo -e "\n${YELLOW}Linking to Railway project...${NC}"
railway link "$PROJECT_ID"

# Pull environment variables
echo -e "\n${YELLOW}Pulling environment variables...${NC}"
railway env pull --yes

# Verify required environment variables
REQUIRED_VARS=(
    "OPENROUTER_API_KEY"
    "TAVILY_API_KEY"
    "ENABLE_SEARCH"
)

echo -e "\n${YELLOW}Verifying environment variables...${NC}"
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo -e "${RED}Error: Missing required variable: $var${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ $var set${NC}"
done

# Deploy using docker-compose
echo -e "\n${YELLOW}Deploying services with docker-compose...${NC}"
railway up --detach

# Wait for services to start
echo -e "\n${YELLOW}Waiting for services to start (30s)...${NC}"
sleep 30

# Health check function
check_health() {
    local service=$1
    local port=$2
    local url="https://${service}.up.railway.app/health"
    
    if curl -sf "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $service:$port - healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ $service:$port - unhealthy${NC}"
        return 1
    fi
}

# Check all services
echo -e "\n${YELLOW}Running health checks...${NC}"
SERVICES=(
    "router:8001"
    "bcra:8002"
    "comex:8003"
    "senasa:8004"
    "auditor:8005"
    "frontend:3000"
)

ALL_HEALTHY=true
for service_port in "${SERVICES[@]}"; do
    IFS=':' read -r service port <<< "$service_port"
    if ! check_health "$service" "$port"; then
        ALL_HEALTHY=false
    fi
done

# Show deployment status
echo -e "\n${YELLOW}Deployment Status:${NC}"
railway status

# Show logs tail
echo -e "\n${YELLOW}Recent logs:${NC}"
railway logs --tail 20

# Final status
if [ "$ALL_HEALTHY" = true ]; then
    echo -e "\n${GREEN}✅ Deployment successful! All services healthy.${NC}"
    echo -e "${GREEN}Router URL: https://router.up.railway.app${NC}"
    echo -e "${GREEN}Frontend URL: https://frontend.up.railway.app${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Deployment completed but some services are unhealthy${NC}"
    echo "Check logs with: railway logs --service <service-name>"
    exit 1
fi