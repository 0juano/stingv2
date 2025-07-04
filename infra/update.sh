#!/bin/bash
# Zero-downtime update script for Proyecto Sting
# Pulls latest code and performs rolling restart

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Change to app directory
APP_DIR="/opt/proyecto-sting"
cd "$APP_DIR"

echo -e "${YELLOW}🔄 Starting update process...${NC}"

# 1. Save current git hash
OLD_HASH=$(git rev-parse HEAD)
echo "Current version: $OLD_HASH"

# 2. Pull latest changes
echo -e "${YELLOW}Pulling latest code...${NC}"
git pull origin main

NEW_HASH=$(git rev-parse HEAD)
echo "New version: $NEW_HASH"

if [ "$OLD_HASH" = "$NEW_HASH" ]; then
    echo -e "${GREEN}Already up to date!${NC}"
    exit 0
fi

# 3. Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Run deploy.sh first"
    exit 1
fi

# 4. Build new images
echo -e "${YELLOW}Building new images...${NC}"
docker-compose build

# 5. Perform rolling restart (zero-downtime)
echo -e "${YELLOW}Performing rolling restart...${NC}"

# Order matters: restart agents first, then router, then frontend
SERVICES=(
    "bcra"
    "comex"
    "senasa"
    "auditor"
    "router"
    "frontend"
)

for service in "${SERVICES[@]}"; do
    echo -e "${YELLOW}Updating $service...${NC}"
    
    # For frontend, we can just restart (nginx handles gracefully)
    if [ "$service" = "frontend" ]; then
        docker-compose up -d --no-deps "$service"
    else
        # For backend services, scale up then down for zero downtime
        # First start new container
        docker-compose up -d --no-deps --scale "$service=2" "$service"
        sleep 5
        
        # Then remove old container
        docker-compose up -d --no-deps --scale "$service=1" "$service"
    fi
    
    # Wait for health check
    port=""
    case $service in
        router) port="8001" ;;
        bcra) port="8002" ;;
        comex) port="8003" ;;
        senasa) port="8004" ;;
        auditor) port="8005" ;;
        frontend) port="80" ;;
    esac
    
    if [ -n "$port" ]; then
        echo -n "Waiting for $service to be healthy..."
        for i in {1..30}; do
            if curl -sf "http://localhost:$port/health" > /dev/null 2>&1 || [ "$service" = "frontend" ]; then
                echo -e " ${GREEN}✓${NC}"
                break
            fi
            echo -n "."
            sleep 1
        done
    fi
done

# 6. Clean up old images
echo -e "${YELLOW}Cleaning up old images...${NC}"
docker image prune -f

# 7. Show status
echo -e "${YELLOW}Checking final status...${NC}"
docker-compose ps

# 8. Show changes
echo -e "\n${GREEN}✅ Update complete!${NC}"
echo -e "${YELLOW}Changes:${NC}"
git log --oneline "$OLD_HASH..$NEW_HASH"

echo -e "\n${YELLOW}Post-update checklist:${NC}"
echo "1. Test frontend: http://$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address 2>/dev/null || echo 'YOUR_SERVER_IP')"
echo "2. Check logs: docker-compose logs -f"
echo "3. Monitor health: ./infra/healthcheck.sh"