# 🚀 Deployment Guide - Bureaucracy Oracle

## Railway Deployment (Recommended)

### Prerequisites
- Railway account (https://railway.app)
- GitHub account
- OpenRouter API key
- Tavily API key

### Step 1: Initial Setup

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
railway login
```

2. **Create Railway Project:**
```bash
railway init
# Save the project ID shown
```

### Step 2: Environment Configuration

1. **Set up environment variables in Railway dashboard:**

Required variables:
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxx
TAVILY_API_KEY=tvly-xxxxx
ENABLE_SEARCH=true
RAILWAY_PROJECT_ID=your-project-id
```

Optional performance settings:
```env
AUTO_SLEEP_MINUTES=10
HEALTH_CHECK_TIMEOUT=30
MAX_RESPONSE_TIME_MS=500
MONTHLY_BUDGET_USD=20
```

### Step 3: Deploy Services

1. **Automatic deployment:**
```bash
./infra/railway.sh <your-project-id>
```

2. **Manual deployment:**
```bash
railway link <project-id>
railway up --detach
```

### Step 4: Configure GitHub Actions

1. **Add secrets to GitHub repository:**
   - Go to Settings → Secrets → Actions
   - Add:
     - `RAILWAY_TOKEN` (from Railway dashboard)
     - `RAILWAY_PROJECT_ID`
     - `OPENROUTER_API_KEY`
     - `TAVILY_API_KEY`

2. **Enable Actions:**
   - Push to `main` branch triggers deployment
   - Tag `v*` creates production release

### Step 5: Verify Deployment

1. **Check service health:**
```bash
./scripts/health-check-all.sh
```

2. **Test Buenos Aires latency:**
```bash
./scripts/ping-buenos-aires.sh
```

3. **Monitor costs:**
```bash
./scripts/cost-monitor.py
```

## Production URLs

After deployment, your services will be available at:

- Frontend: `https://bureaucracy-oracle.up.railway.app`
- API Router: `https://router.up.railway.app`
- API Documentation: `https://router.up.railway.app/docs`

Internal services (not publicly accessible):
- BCRA: `bcra.railway.internal:8002`
- Comex: `comex.railway.internal:8003`
- Senasa: `senasa.railway.internal:8004`

## Cost Management

### Estimated Monthly Costs (Railway Hobby Plan)
- CPU: ~$5-8
- Memory: ~$3-5
- Network: ~$2-4
- **Total: ~$10-17/month**

### Cost Optimization Tips

1. **Enable auto-sleep:**
   - Services sleep after 10 minutes idle
   - Saves ~70% on costs

2. **Use caching:**
   - Tavily search results cached for 24 hours
   - Reduces API calls

3. **Monitor usage:**
   ```bash
   # Run daily
   ./scripts/cost-monitor.py
   ```

## Monitoring & Maintenance

### Health Monitoring

1. **Automated health checks:**
   - Railway runs `/health` checks every 30s
   - Auto-restarts unhealthy services

2. **Manual monitoring:**
   ```bash
   # Check all services
   railway status
   
   # View logs
   railway logs --service router --tail 100
   ```

### Performance Monitoring

1. **Latency targets:**
   - Buenos Aires average: <170ms
   - p95 response time: <500ms

2. **Check performance:**
   ```bash
   # Test from Buenos Aires
   ./scripts/ping-buenos-aires.sh
   
   # Results saved to logs/latency-*.json
   ```

### Troubleshooting

**Services not starting:**
```bash
# Check logs
railway logs --service <service-name>

# Verify environment variables
railway variables
```

**High latency:**
- Check Railway region settings
- Verify service resource allocation
- Review recent deployments

**Cost overruns:**
- Enable auto-sleep
- Reduce service resources
- Check for runaway queries

## Security Best Practices

1. **API Keys:**
   - Never commit to repository
   - Rotate keys monthly
   - Use Railway's secret management

2. **Access Control:**
   - Internal services not exposed
   - CORS configured for frontend only
   - Health endpoints are public

3. **Monitoring:**
   - Set up alerts for failures
   - Monitor for unusual usage
   - Track API costs

## Rollback Procedure

If deployment fails:

1. **Quick rollback:**
   ```bash
   railway rollback
   ```

2. **Manual rollback:**
   - Go to Railway dashboard
   - Select deployment history
   - Click "Rollback" on last working version

## Alternative Platforms

### Render
```yaml
# render.yaml
services:
  - type: web
    name: router
    env: docker
    dockerfilePath: ./agents/router/Dockerfile
    envVars:
      - key: OPENROUTER_API_KEY
        fromDatabase: false
```

### Fly.io
```toml
# fly.toml
app = "bureaucracy-oracle"
kill_signal = "SIGINT"
kill_timeout = 5

[env]
  PORT = "8000"

[experimental]
  allowed_public_ports = []
  auto_rollback = true
```

### DigitalOcean App Platform
- Use App Platform UI
- Connect GitHub repository
- Configure environment variables
- Deploy

---

For questions or issues, check the [troubleshooting guide](#troubleshooting) or open an issue on GitHub.