# Architecture Recommendations for Bureaucracy Oracle

## Executive Summary

The current Docker microservices architecture is causing significant development friction without providing proportional benefits. I recommend migrating to a **single FastAPI backend with async parallelism** paired with modern deployment platforms that eliminate manual server management.

## Current Architecture Pain Points

### 1. **Development Workflow Issues**
- Every UI change requires Docker rebuilds
- Multiple containers complicate debugging
- Resource-heavy local development (6 containers)
- Frontend changes break unexpectedly

### 2. **Deployment Complexity**
- Manual SSH deployments to DigitalOcean
- Environment variables differ between local/prod
- Docker-compose recreation errors
- Complex firewall and port management

### 3. **Maintenance Overhead**
- 6 separate services to maintain
- Dockerfile changes cascade failures
- Network issues between containers
- Difficult to trace request flows

## Recommended Architecture: Monolithic Async FastAPI

### Core Design
```python
# Single FastAPI app with async parallelism
app = FastAPI()

@app.post("/api/query")
async def query(payload: dict):
    # Route to appropriate agents
    routing = await route_query(payload["question"])
    
    # Execute agents in parallel (no Docker needed!)
    results = await asyncio.gather(
        *[process_agent(agent, payload["question"]) 
          for agent in routing["agents"]]
    )
    
    # Audit and return
    return await audit_responses(results)
```

### Key Benefits
1. **Maintains parallel execution** via Python's `asyncio`
2. **Single process** = easier debugging
3. **Instant UI updates** with Vite hot reload
4. **One `.env` file** that works everywhere
5. **Simplified deployment** with modern platforms

## Implementation Plan

### Phase 1: Local Development Simplification

#### Backend Structure
```
backend/
├── main.py           # FastAPI app
├── agents/
│   ├── router.py     # Query routing logic
│   ├── bcra.py       # BCRA agent logic
│   ├── comex.py      # Comex agent logic
│   ├── senasa.py     # Senasa agent logic
│   └── auditor.py    # Response auditing
├── config.py         # Environment config
├── requirements.txt
└── .env
```

#### Frontend Development
```bash
# No Docker needed!
cd frontend && npm run dev  # Instant hot reload
cd backend && uvicorn main:app --reload  # Auto-restart on changes
```

### Phase 2: Modern Deployment Options

#### Option A: Railway.app (Recommended)
**Pros:**
- One-click deploys from GitHub
- Automatic SSL certificates
- Built-in environment variable management
- $5/month for small apps
- Zero DevOps knowledge required

**Setup:**
```bash
# Install CLI
npm install -g @railway/cli

# Deploy
railway login
railway up
```

#### Option B: Render.com
**Pros:**
- Free tier available
- Auto-deploys on git push
- Dashboard for env vars
- Built-in logging

**Setup:**
1. Connect GitHub repo
2. Set environment variables in dashboard
3. Every push auto-deploys

#### Option C: Vercel (Frontend) + Modal (Backend)
**Pros:**
- Serverless = infinite scale
- Pay only for usage
- Zero infrastructure management

**Backend with Modal:**
```python
import modal

stub = modal.Stub("bureaucracy-oracle")

@stub.function(
    secrets=[modal.Secret.from_name("openrouter-api")],
    timeout=30
)
@modal.web_endpoint()
async def query(payload: dict):
    # Your async agent logic here
    return response
```

### Phase 3: If Staying with DigitalOcean

#### Use App Platform Instead of Droplets
```yaml
# app.yaml
name: bureaucracy-oracle
services:
- name: api
  github:
    repo: yourusername/bureaucracy-oracle
    branch: main
  source_dir: backend
  run_command: uvicorn main:app --host 0.0.0.0
  envs:
  - key: OPENROUTER_API_KEY
    scope: RUN_TIME
    type: SECRET

- name: frontend
  github:
    repo: yourusername/bureaucracy-oracle
    branch: main
  source_dir: frontend
  build_command: npm run build
  run_command: npm start
```

#### Or Simplify Droplet Deployment
```bash
#!/bin/bash
# deploy.sh - One-command deployment

# On your local machine
rsync -avz --exclude 'node_modules' --exclude '.env' . root@your-droplet:/opt/app/
ssh root@your-droplet "cd /opt/app && ./remote-deploy.sh"

# remote-deploy.sh (on server)
#!/bin/bash
source /opt/app/.env.production
pip install -r requirements.txt
npm --prefix frontend install
npm --prefix frontend run build
systemctl restart bureaucracy-oracle
```

## Migration Checklist

- [ ] **Week 1: Consolidate Backend**
  - [ ] Create single FastAPI app with all agents
  - [ ] Implement async parallel execution
  - [ ] Test locally without Docker
  - [ ] Verify performance is maintained

- [ ] **Week 2: Simplify Frontend**
  - [ ] Remove Docker from frontend development
  - [ ] Set up Vite proxy to backend
  - [ ] Test hot reload functionality
  - [ ] Fix any CORS issues

- [ ] **Week 3: Environment Management**
  - [ ] Create unified config.py with pydantic
  - [ ] Single .env file for all settings
  - [ ] Document all required variables
  - [ ] Test in development and staging

- [ ] **Week 4: Deploy to Modern Platform**
  - [ ] Choose platform (Railway recommended)
  - [ ] Set up GitHub integration
  - [ ] Configure environment variables
  - [ ] Test production deployment
  - [ ] Set up monitoring

## Cost Comparison

| Solution | Monthly Cost | Complexity | Auto-Deploy | Scaling |
|----------|-------------|------------|-------------|---------|
| Current (DigitalOcean Droplet) | $20-40 | High | No | Manual |
| Railway | $5-20 | Low | Yes | Automatic |
| Render | $0-25 | Low | Yes | Automatic |
| Vercel + Modal | $0-20 | Medium | Yes | Infinite |
| DigitalOcean App Platform | $12-40 | Medium | Yes | Automatic |

## Conclusion

The current Docker microservices architecture adds complexity without providing necessary benefits for this application. A monolithic async FastAPI backend maintains all the parallelism benefits while dramatically simplifying:

1. **Development** - No Docker rebuilds for UI changes
2. **Deployment** - One-click deploys with modern platforms
3. **Maintenance** - Single codebase, unified logging
4. **Costs** - Potentially lower with efficient platforms

The migration can be done incrementally, starting with local development improvements and moving to production deployment enhancements.

## Next Steps

1. **Immediate**: Remove Docker from frontend development
2. **This Week**: Create proof-of-concept single backend
3. **Next Sprint**: Choose and test deployment platform
4. **Within Month**: Complete migration

This approach will make the codebase a joy to work with while maintaining all current functionality.