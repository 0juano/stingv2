# Railway Multi-Service Deployment Guide

## Overview
This project requires deploying 5 separate services on Railway. Each service runs independently and communicates via Railway's internal networking.

## Services to Deploy

1. **Router** - Main API gateway (port 8001)
2. **BCRA** - Central Bank agent (port 8002)
3. **Comex** - Foreign trade agent (port 8003)
4. **Senasa** - Agricultural agent (port 8004)
5. **Auditor** - Response validator (port 8005)

## Step-by-Step Deployment

### 1. Delete the Current Failed Service
- Go to Railway dashboard
- Click on "scintillating-miracle" 
- Go to Settings → Danger → Delete Service

### 2. Create Services in Railway

You need to create 5 separate services. For each service:

#### Option A: Using Railway Dashboard (Easier)

1. Click "New" → "GitHub Repo"
2. Select your repository: `0juano/stingv2`
3. Name the service (e.g., "router", "bcra", etc.)
4. **IMPORTANT**: Set the "Root Directory" to:
   - Router: `/agents/router`
   - BCRA: `/agents/bcra`
   - Comex: `/agents/comex`
   - Senasa: `/agents/senasa`
   - Auditor: `/agents/auditor`

#### Option B: Using Railway CLI

```bash
# Create each service
railway service create router
railway service create bcra
railway service create comex
railway service create senasa
railway service create auditor
```

### 3. Configure Environment Variables

For **ALL services**, add these variables:
```
OPENROUTER_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
ENABLE_SEARCH=true
```

For the **Router service**, also add:
```
BCRA_SERVICE_URL=http://bcra.railway.internal
COMEX_SERVICE_URL=http://comex.railway.internal
SENASA_SERVICE_URL=http://senasa.railway.internal
AUDITOR_SERVICE_URL=http://auditor.railway.internal
```

### 4. Configure Service URLs

Each service needs to be accessible:

1. **Router** - Make it public (it's your main API)
   - In service settings, add a domain
   - Railway will provide something like: `router-production.up.railway.app`

2. **Other services** - Keep them internal (private)
   - They'll be accessible via: `servicename.railway.internal`

### 5. Deploy

Once configured, each service will automatically deploy. Monitor the logs to ensure they start correctly.

## Testing

Once all services are deployed:

```bash
# Test the router health
curl https://router-production.up.railway.app/health

# Test a query
curl -X POST https://router-production.up.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cómo exportar limones?"}'
```

## Troubleshooting

- **Service can't find other services**: Check internal URLs in Router's environment variables
- **Build failures**: Each service has its own Dockerfile and requirements.txt
- **High costs**: You're running 5 services - monitor usage in Railway dashboard

## Architecture Diagram

```
Internet
    ↓
[Router] (public)
    ↓
Internal Network (railway.internal)
    ├── [BCRA]
    ├── [Comex]
    ├── [Senasa]
    └── [Auditor]
```

## Important Notes

- This is the proper way to deploy microservices on Railway
- Each service runs in its own container with dedicated resources
- Internal communication uses Railway's private network
- Only the Router needs public access