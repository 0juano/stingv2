# Steps to Fix the Remote Server

## Problem Summary
The remote server (147.182.248.187) is failing because:
1. The router code has the old error handling that hides real errors
2. Most likely the .env file with API keys is missing or not loaded

## Step 1: Push and Deploy the Updated Code

First, commit and push the changes:
```bash
git add .
git commit -m "fix: improve router error handling and fix NoneType issues"
git push origin main
```

## Step 2: Update the Remote Server

SSH into the server and update the code:
```bash
ssh root@147.182.248.187
cd /opt/proyecto-sting

# Pull the latest code
git pull origin main

# Check if .env file exists
ls -la .env
```

## Step 3: Create/Update the .env File (if missing)

If the .env file is missing, create it:
```bash
nano .env
```

Add these lines:
```
# OpenRouter API Configuration
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY_HERE

# Tavily Search API Configuration  
TAVILY_API_KEY=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

# Feature Flags
ENABLE_SEARCH=false
```

Save and exit (Ctrl+X, then Y, then Enter).

## Step 4: Rebuild and Restart Services

```bash
# Rebuild the router service with new code
docker-compose build router

# Restart all services
docker-compose down
docker-compose up -d

# Check if services are running
docker ps

# Check router logs to see the actual error
docker logs router --tail 50
```

## Step 5: Test the Fix

From your local machine, test:
```bash
curl -X POST http://147.182.248.187:8001/route \
  -H "Content-Type: application/json" \
  -d '{"question":"¿Cuál es el límite para pagos al exterior?"}' | jq .
```

You should now see either:
- A successful response with the correct agent (bcra)
- A specific error message (like "API key inválida" instead of generic error)

## Expected Results

If the .env file was missing, you'll see an error about the API key.
Once the .env file is in place and services are restarted, it should work correctly.

## Troubleshooting

If it still doesn't work after these steps:

1. Check if the containers have the environment variables:
```bash
docker exec router env | grep OPENROUTER
```

2. Test connectivity from the container:
```bash
docker exec router curl -I https://openrouter.ai
```

3. Check detailed logs:
```bash
docker logs router --tail 100 | grep -i error
```