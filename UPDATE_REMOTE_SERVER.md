# Update Remote Server - Quick Steps

## 1. SSH into DigitalOcean server
```bash
ssh root@147.182.248.187
```

## 2. Navigate to project directory
```bash
cd /opt/proyecto-sting
```

## 3. Update the .env file with new API key
```bash
nano .env
```

Replace the OPENROUTER_API_KEY line with:
```
OPENROUTER_API_KEY=YOUR_NEW_OPENROUTER_API_KEY_HERE
```

Save and exit (Ctrl+X, then Y, then Enter)

## 4. Pull latest code from GitHub
```bash
git pull origin main
```

## 5. Restart Docker containers
```bash
docker-compose down
docker-compose up -d --build
```

## 6. Verify services are running
```bash
docker ps
```

You should see all 6 containers running:
- frontend
- router
- bcra
- comex
- senasa
- auditor

## 7. Test the API
```bash
curl -X POST http://localhost:8001/route \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
```

Should return a JSON response without errors.

## Done!
The site should now be working at http://147.182.248.187/