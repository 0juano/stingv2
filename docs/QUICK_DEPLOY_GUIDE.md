# Quick Deploy Guide - Remaining Services

## Services to Deploy
1. **bcra** - Central Bank agent
2. **comex** - Foreign trade agent  
3. **senasa** - Agricultural agent
4. **auditor** - Response validator

## For Each Service, Do This:

### Step 1: Create New Service in Railway
1. Go to Railway dashboard
2. Click "New" → "Empty Service"
3. Name it (bcra, comex, senasa, or auditor)

### Step 2: Connect GitHub
1. In the service, click "Connect GitHub repo"
2. Select your repository: `0juano/stingv2`
3. **IMPORTANT**: Set "Root Directory" to:
   - For BCRA: `/agents/bcra`
   - For Comex: `/agents/comex`
   - For Senasa: `/agents/senasa`
   - For Auditor: `/agents/auditor`

### Step 3: Add Environment Variables
Go to Variables tab and add:
```
OPENROUTER_API_KEY=(your key from .env)
TAVILY_API_KEY=(your key from .env)
ENABLE_SEARCH=true
```

### Step 4: Configure Networking (Internal Services Only)
These services should NOT have public URLs - they're internal only.
No need to generate domains for bcra, comex, senasa, auditor.

### Step 5: Deploy
The service will auto-deploy after connecting GitHub.

## After All Services Are Deployed:

### Configure Router Service
In your **router** service (cardo), go to Variables and add:
```
BCRA_SERVICE_URL=http://bcra.railway.internal
COMEX_SERVICE_URL=http://comex.railway.internal
SENASA_SERVICE_URL=http://senasa.railway.internal
AUDITOR_SERVICE_URL=http://auditor.railway.internal
```

## Test Commands:
```bash
# Test routing
curl -X POST https://cardo.up.railway.app/route \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cómo exportar limones?"}'

# Test full query
curl -X POST https://cardo.up.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuál es el límite para comprar dólares?"}'
```

## Service Order:
1. Deploy bcra first
2. Then comex
3. Then senasa
4. Then auditor
5. Finally update router with the internal URLs