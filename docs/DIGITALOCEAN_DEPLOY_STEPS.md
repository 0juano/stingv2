# 🚀 Proyecto Sting - DigitalOcean Deployment Steps

## Prerequisites
- [ ] Have your OpenRouter API key ready
- [ ] Have your Tavily API key ready
- [ ] Have your GitHub repo URL ready

## Step 1: Create DigitalOcean Account (3 min)
1. [ ] Go to https://digitalocean.com
2. [ ] Sign up (use GitHub for faster signup)
3. [ ] Enter credit card (you get $200 free credit for 60 days)

## Step 2: Create Docker Droplet (5 min)

1. [ ] Click green "Create" button → "Droplets"

2. [ ] **Choose an image:**
   - Click "Marketplace"
   - Search for "Docker"
   - Select "Docker on Ubuntu 22.04"

3. [ ] **Choose a plan:**
   - Droplet Type: Basic
   - CPU: Regular (Intel with SSD)
   - Size: $12/mo (2 GB RAM / 1 CPU / 50 GB SSD)

4. [ ] **Choose datacenter:**
   - Region: New York (or closest to Argentina)

5. [ ] **Authentication:**
   - Password (easier for now)
   - Create a strong root password

6. [ ] **Finalize:**
   - Hostname: `proyecto-sting`
   - Tags: `production`
   - Click "Create Droplet"

7. [ ] **Save your credentials:**
   ```
   IP Address: _____________ (shown after creation)
   Root Password: _____________ (what you just set)
   ```

## Step 3: Connect & Deploy (10 min)

1. [ ] Open Terminal on your Mac

2. [ ] SSH into your server:
   ```bash
   ssh root@YOUR_IP_ADDRESS
   # Enter password when prompted
   ```

3. [ ] Set your API keys:
   ```bash
   export OPENROUTER_API_KEY="sk-or-v1-your-actual-key-here"
   export TAVILY_API_KEY="tvly-your-actual-key-here"
   export GITHUB_REPO_URL="https://github.com/yourusername/stingv2.git"
   ```

4. [ ] Download and run deployment:
   ```bash
   # Download deploy script
   curl -o deploy.sh https://raw.githubusercontent.com/yourusername/stingv2/main/infra/deploy.sh
   
   # Make it executable
   chmod +x deploy.sh
   
   # Run deployment
   ./deploy.sh
   ```

5. [ ] Wait for "✅ Deployment successful!" message

## Step 4: Verify It Works (2 min)

1. [ ] Test API health:
   ```bash
   curl http://YOUR_IP_ADDRESS:8001/health
   # Should return: {"status":"ok"}
   ```

2. [ ] Open in browser:
   - [ ] Frontend: `http://YOUR_IP_ADDRESS`
   - [ ] API Docs: `http://YOUR_IP_ADDRESS:8001/docs`

3. [ ] Test a query in the terminal interface:
   - Type: "¿Cómo importar laptops desde USA?"
   - Should get a response about import requirements

## Step 5: Set Up Monitoring (Optional - 5 min)

1. [ ] Start health monitoring:
   ```bash
   cd /opt/proyecto-sting
   ./infra/healthcheck.sh -d
   ```

2. [ ] Set up auto-start on reboot:
   ```bash
   # Add to crontab
   crontab -e
   # Add this line:
   @reboot cd /opt/proyecto-sting && docker-compose up -d
   ```

## Step 6: Save Important Info

Copy this to a secure location:
```
Server IP: _________________
Root Password: _________________
Deploy Date: _________________

SSH Command: ssh root@YOUR_IP

Update Command: 
cd /opt/proyecto-sting && ./infra/update.sh

View Logs:
cd /opt/proyecto-sting && docker-compose logs -f

Restart Services:
cd /opt/proyecto-sting && docker-compose restart
```

## Troubleshooting

**"Connection refused" error:**
- Services take ~30 seconds to start
- Check logs: `docker-compose logs router`

**"API key not set" error:**
- Make sure you exported the variables before running deploy.sh
- Check .env file exists: `cat /opt/proyecto-sting/.env`

**Frontend shows error:**
- Check all services are running: `docker-compose ps`
- All should show "Up" status

## Total Time: ~20 minutes

✅ That's it! Your app is now live at `http://YOUR_IP_ADDRESS`

## Next Steps (When Ready)

1. **Add a domain name:**
   - Buy domain (e.g., sting.com.ar)
   - Point A record to your IP address

2. **Enable HTTPS:**
   - We'll add Let's Encrypt later

3. **Set up backups:**
   - DigitalOcean automated backups ($2/month)