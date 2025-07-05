# Deploy Instructions

## Step 1: SSH into your server
```bash
ssh root@147.182.248.187
```

## Step 2: Run this command
```bash
cd /opt/proyecto-sting && \
git pull origin main && \
nano .env
```

## Step 3: When nano opens, paste this:
```
OPENROUTER_API_KEY=YOUR_NEW_API_KEY_HERE
TAVILY_API_KEY=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
ENABLE_SEARCH=true
```

Replace YOUR_NEW_API_KEY_HERE with your actual new API key.

## Step 4: Save and exit nano
- Press Ctrl+X
- Press Y
- Press Enter

## Step 5: Restart Docker
```bash
docker-compose down && docker-compose up -d --build
```

That's it!