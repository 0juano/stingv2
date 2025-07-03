# Manual Deployment Steps for Proyecto-Sting

## 1. Link to Project (Run in Terminal)
```bash
railway link
# Select: 0juano's Projects → Proyecto-Sting
```

## 2. Set Environment Variables (Run these commands)
```bash
# Load your local environment
source .env

# Set variables in Railway
railway variables set OPENROUTER_API_KEY="$OPENROUTER_API_KEY"
railway variables set TAVILY_API_KEY="$TAVILY_API_KEY"
railway variables set ENABLE_SEARCH="true"
```

## 3. Deploy
```bash
railway up
```

## 4. Monitor Deployment
```bash
# Watch logs
railway logs -f

# Check status
railway status
```

## Alternative: Use Railway Dashboard

1. Go to https://railway.app/dashboard
2. Click on "Proyecto-Sting"
3. Go to Variables tab
4. Add these variables:
   - OPENROUTER_API_KEY = (your key from .env)
   - TAVILY_API_KEY = (your key from .env)
   - ENABLE_SEARCH = true
5. Go to Settings → Triggers
6. Click "Deploy" or push to GitHub to trigger automatic deployment

The app will be available at your Railway domain once deployed!