#!/bin/bash
# DigitalOcean Docker 1-Click Deployment Script
# Deploys Bureaucracy Oracle in < 10 minutes

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Deploying Proyecto Sting${NC}"

# 1. Check if we're on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release; then
    echo -e "${RED}Error: This script is designed for Ubuntu 22.04${NC}"
    exit 1
fi

# 2. Check if Docker is installed (should be on Docker 1-Click)
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker not found. Use DigitalOcean Docker 1-Click image${NC}"
    exit 1
fi

# 3. Clone repository
REPO_URL="${GITHUB_REPO_URL:-https://github.com/yourusername/stingv2.git}"
APP_DIR="/opt/proyecto-sting"

if [ -d "$APP_DIR" ]; then
    echo -e "${YELLOW}Updating existing installation...${NC}"
    cd "$APP_DIR"
    git pull origin main
else
    echo -e "${YELLOW}Cloning repository...${NC}"
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

# 4. Create .env file
echo -e "${YELLOW}Setting up environment variables...${NC}"
if [ -z "${OPENROUTER_API_KEY:-}" ] || [ -z "${TAVILY_API_KEY:-}" ]; then
    echo -e "${RED}Error: API keys not set${NC}"
    echo "Please run:"
    echo "  export OPENROUTER_API_KEY='your-key'"
    echo "  export TAVILY_API_KEY='your-key'"
    echo "Then run this script again"
    exit 1
fi

cat > .env << EOF
# API Keys
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
TAVILY_API_KEY=${TAVILY_API_KEY}

# Service Configuration
ENABLE_SEARCH=true
OPENROUTER_MODEL=openai/gpt-4o-mini

# Router Biases
ROUTER_BIAS_BCRA=1.2
ROUTER_BIAS_COMEX=0.9
ROUTER_BIAS_SENASA=1.0
EOF

# 5. Stop any existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true

# 6. Pull latest images and start services
echo -e "${YELLOW}Starting services...${NC}"
docker-compose up -d --build

# 7. Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to start (30s)...${NC}"
sleep 30

# 8. Health check
echo -e "${YELLOW}Checking service health...${NC}"
SERVICES=(
    "router:8001"
    "bcra:8002"
    "comex:8003"
    "senasa:8004"
    "auditor:8005"
)

ALL_HEALTHY=true
for service_port in "${SERVICES[@]}"; do
    IFS=':' read -r service port <<< "$service_port"
    if curl -sf "http://localhost:$port/health" > /dev/null; then
        echo -e "${GREEN}✓ $service (port $port) - healthy${NC}"
    else
        echo -e "${RED}✗ $service (port $port) - not responding${NC}"
        ALL_HEALTHY=false
    fi
done

# 9. Get server IP
SERVER_IP=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address 2>/dev/null || echo "YOUR_SERVER_IP")

# 10. Final status
if [ "$ALL_HEALTHY" = true ]; then
    echo -e "\n${GREEN}✅ Deployment successful!${NC}"
    echo -e "${GREEN}Frontend: http://$SERVER_IP${NC}"
    echo -e "${GREEN}API: http://$SERVER_IP:8001${NC}"
    echo -e "\nTest with: curl http://$SERVER_IP:8001/health"
else
    echo -e "\n${YELLOW}⚠️  Some services may need more time to start${NC}"
    echo "Check logs with: docker-compose logs -f"
fi

echo -e "\n${YELLOW}Useful commands:${NC}"
echo "  cd $APP_DIR"
echo "  docker-compose logs -f     # View logs"
echo "  docker-compose ps          # Check status"
echo "  docker-compose restart     # Restart services"