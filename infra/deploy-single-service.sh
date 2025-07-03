#!/usr/bin/env bash
# Deploy as a single monolithic service to Railway (for free tier)
# This runs all agents in a single container using orchestrator

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚂 Railway Single Service Deployment${NC}"
echo "Deploying Bureaucracy Oracle as a monolithic service"
echo ""

# Note about environment variables
echo -e "${YELLOW}Note: You'll need to set environment variables in Railway dashboard${NC}"

# Create a Dockerfile for the monolithic deployment
echo -e "${YELLOW}Creating monolithic Dockerfile...${NC}"
cat > Dockerfile.railway <<'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all agent code
COPY agents/ ./agents/
COPY orchestrator.py .
COPY orchestrator_multiagent.py .
COPY agents.yml .

# Create a startup script
RUN echo '#!/bin/bash\n\
cd /app\n\
# Start all services in background\n\
cd agents/router && uvicorn main:app --host 0.0.0.0 --port 8001 &\n\
cd /app/agents/bcra && uvicorn main:app --host 0.0.0.0 --port 8002 &\n\
cd /app/agents/comex && uvicorn main:app --host 0.0.0.0 --port 8003 &\n\
cd /app/agents/senasa && uvicorn main:app --host 0.0.0.0 --port 8004 &\n\
cd /app/agents/auditor && uvicorn main:app --host 0.0.0.0 --port 8005 &\n\
# Keep container running\n\
wait' > /start.sh && chmod +x /start.sh

EXPOSE 8001 8002 8003 8004 8005

CMD ["/start.sh"]
EOF

# Create Railway configuration
echo -e "${YELLOW}Creating Railway configuration...${NC}"
cat > railway.json <<EOF
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "./Dockerfile.railway"
  },
  "deploy": {
    "startCommand": "/start.sh",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3,
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30
  }
}
EOF

# Create a simple web server that proxies to router
echo -e "${YELLOW}Creating proxy server...${NC}"
cat > proxy.py <<'EOF'
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import os

app = FastAPI()

ROUTER_URL = "http://localhost:8001"

@app.get("/")
async def root():
    return {"message": "Bureaucracy Oracle API", "router": f"{ROUTER_URL}/docs"}

@app.get("/health")
async def health():
    # Check all services
    services = {
        "router": 8001,
        "bcra": 8002,
        "comex": 8003,
        "senasa": 8004,
        "auditor": 8005
    }
    
    status = {}
    for service, port in services.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:{port}/health")
                status[service] = response.status_code == 200
        except:
            status[service] = False
    
    all_healthy = all(status.values())
    return JSONResponse(
        content={"services": status, "healthy": all_healthy},
        status_code=200 if all_healthy else 503
    )

@app.post("/query")
async def query(request: Request):
    # Proxy to router
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{ROUTER_URL}/query", json=body)
        return response.json()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

# Update startup script to include proxy
echo -e "${YELLOW}Updating startup script...${NC}"
cat > Dockerfile.railway <<'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install httpx

# Copy all code
COPY agents/ ./agents/
COPY orchestrator.py .
COPY orchestrator_multiagent.py .
COPY agents.yml .
COPY proxy.py .

# Create startup script
RUN echo '#!/bin/bash\n\
cd /app\n\
# Start all services in background\n\
cd agents/router && uvicorn main:app --host 0.0.0.0 --port 8001 &\n\
cd /app/agents/bcra && uvicorn main:app --host 0.0.0.0 --port 8002 &\n\
cd /app/agents/comex && uvicorn main:app --host 0.0.0.0 --port 8003 &\n\
cd /app/agents/senasa && uvicorn main:app --host 0.0.0.0 --port 8004 &\n\
cd /app/agents/auditor && uvicorn main:app --host 0.0.0.0 --port 8005 &\n\
sleep 5\n\
# Start proxy on Railway PORT\n\
cd /app && python proxy.py' > /start.sh && chmod +x /start.sh

EXPOSE 8000

CMD ["/start.sh"]
EOF

echo -e "\n${GREEN}✅ Configuration created!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Commit these new files:"
echo "   git add Dockerfile.railway railway.json proxy.py"
echo "   git commit -m 'Add Railway monolithic deployment'"
echo "   git push"
echo ""
echo "2. In Railway dashboard:"
echo "   - Delete the failed project"
echo "   - Create a new project"
echo "   - Import from GitHub"
echo "   - Add environment variables:"
echo "     • OPENROUTER_API_KEY"
echo "     • TAVILY_API_KEY" 
echo "     • ENABLE_SEARCH=true"
echo ""
echo "3. Railway will automatically deploy using Dockerfile.railway"
echo ""
echo -e "${BLUE}This approach runs all services in one container${NC}"
echo "Perfect for Railway's free tier!"