# Domain Setup Guide for proyecto-sting.xyz

## Overview
This guide walks through setting up proyecto-sting.xyz with SSL certificates, proper nginx configuration, and secure API routing on your DigitalOcean droplet.

## Prerequisites
- Domain purchased from Porkbun (proyecto-sting.xyz)
- DigitalOcean droplet running at 147.182.248.187
- SSH access to the droplet
- Application running with Docker Compose

## Phase 1: DNS Configuration on Porkbun

### 1.1 Add DNS Records
Log into Porkbun and add the following DNS records:

| Type | Host | Answer | TTL |
|------|------|--------|-----|
| A | @ | 147.182.248.187 | 600 |
| A | www | 147.182.248.187 | 600 |
| A | api | 147.182.248.187 | 600 |

**Note**: Using 600 seconds (10 minutes) TTL during setup for faster propagation. Can increase to 86400 (24 hours) after setup is complete.

### 1.2 Verify DNS Propagation
```bash
# Check if DNS is propagating (run from your local machine)
dig proyecto-sting.xyz
dig www.proyecto-sting.xyz
dig api.proyecto-sting.xyz

# Or use online tools like whatsmydns.net
```

## Phase 2: SSL Certificate Setup

### 2.1 Install Certbot on Droplet
```bash
# SSH into your droplet
ssh root@147.182.248.187

# Update and install certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### 2.2 Create Nginx Configuration
First, create a new nginx configuration file:

```bash
# Create nginx config directory if it doesn't exist
mkdir -p /opt/proyecto-sting/nginx

# Create the domain configuration
cat > /opt/proyecto-sting/nginx/proyecto-sting.conf << 'EOF'
# HTTP server - redirects to HTTPS
server {
    listen 80;
    server_name proyecto-sting.xyz www.proyecto-sting.xyz;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server - main site
server {
    listen 443 ssl http2;
    server_name proyecto-sting.xyz www.proyecto-sting.xyz;
    
    # SSL certificates (will be added by certbot)
    # ssl_certificate /etc/letsencrypt/live/proyecto-sting.xyz/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/proyecto-sting.xyz/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # HSTS (uncomment after testing)
    # add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Proxy to frontend container
    location / {
        proxy_pass http://localhost:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# API subdomain
server {
    listen 80;
    server_name api.proyecto-sting.xyz;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name api.proyecto-sting.xyz;
    
    # SSL certificates (will be added by certbot)
    # ssl_certificate /etc/letsencrypt/live/api.proyecto-sting.xyz/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/api.proyecto-sting.xyz/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # CORS headers
    add_header Access-Control-Allow-Origin "https://proyecto-sting.xyz" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization" always;
    
    # Handle preflight requests
    if ($request_method = OPTIONS) {
        add_header Access-Control-Allow-Origin "https://proyecto-sting.xyz";
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization";
        add_header Access-Control-Max-Age 1728000;
        add_header Content-Type "text/plain charset=UTF-8";
        add_header Content-Length 0;
        return 204;
    }
    
    # Router service
    location /route {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Auditor service endpoints
    location ~ ^/(audit|audit-multi|format) {
        proxy_pass http://localhost:8005;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Agent services - not exposed directly through API subdomain
    # Clients should go through the router service
}
EOF
```

### 2.3 Install Nginx and Link Configuration
```bash
# Install nginx if not already installed
sudo apt install nginx -y

# Stop nginx temporarily
sudo systemctl stop nginx

# Link the configuration
sudo ln -sf /opt/proyecto-sting/nginx/proyecto-sting.conf /etc/nginx/sites-enabled/

# Remove default site if exists
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Start nginx
sudo systemctl start nginx
```

### 2.4 Obtain SSL Certificates
```bash
# Get certificates for all domains
sudo certbot --nginx -d proyecto-sting.xyz -d www.proyecto-sting.xyz -d api.proyecto-sting.xyz

# Follow the prompts:
# - Enter email address
# - Agree to terms
# - Choose whether to share email
# - Certbot will automatically update nginx config
```

### 2.5 Set Up Auto-Renewal
```bash
# Test auto-renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal (certbot usually does this automatically)
# Check if it exists:
sudo crontab -l | grep certbot

# If not present, add it:
echo "0 0,12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## Phase 3: Update Application Configuration

### 3.1 Create Production Docker Compose Override
```bash
cd /opt/proyecto-sting

# Create production override file
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  # Frontend with domain-aware build
  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_BASE_URL: https://api.proyecto-sting.xyz
    ports:
      - "127.0.0.1:80:80"  # Only listen on localhost
    
  # Router - only accessible internally
  router:
    ports:
      - "127.0.0.1:8001:8000"
      
  # BCRA Agent - only accessible internally
  bcra:
    ports:
      - "127.0.0.1:8002:8000"
      
  # Comex Agent - only accessible internally
  comex:
    ports:
      - "127.0.0.1:8003:8000"
      
  # Senasa Agent - only accessible internally
  senasa:
    ports:
      - "127.0.0.1:8004:8000"
      
  # Auditor - only accessible internally
  auditor:
    ports:
      - "127.0.0.1:8005:8000"
EOF
```

### 3.2 Create Domain-Aware Deployment Script
```bash
cat > deploy-domain.sh << 'EOF'
#!/bin/bash

# Domain-aware deployment script for proyecto-sting.xyz
# Usage: ./deploy-domain.sh

echo "🚀 Starting domain deployment..."

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin main

# Use production override
echo "🔧 Setting up production configuration..."
cp docker-compose.prod.yml docker-compose.override.yml

# Rebuild frontend with domain URL
echo "🔨 Rebuilding frontend for production..."
docker-compose build --no-cache frontend

# Restart services
echo "♻️  Restarting services..."
docker-compose down
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check status
echo "✅ Checking service status..."
docker-compose ps

# Test endpoints
echo "🧪 Testing endpoints..."
echo -n "Frontend (https://proyecto-sting.xyz): "
curl -s -o /dev/null -w "%{http_code}" https://proyecto-sting.xyz
echo ""

echo -n "API (https://api.proyecto-sting.xyz/route): "
curl -s -o /dev/null -w "%{http_code}" https://api.proyecto-sting.xyz/route
echo ""

echo "🎉 Domain deployment complete!"
echo "🌐 Your site is now available at https://proyecto-sting.xyz"
EOF

chmod +x deploy-domain.sh
```

## Phase 4: Security Hardening

### 4.1 Update Firewall Rules
```bash
# Check current UFW status
sudo ufw status

# Allow HTTPS
sudo ufw allow 443/tcp

# Remove direct access to API ports from external IPs
sudo ufw delete allow 8001
sudo ufw delete allow 8002
sudo ufw delete allow 8003
sudo ufw delete allow 8004
sudo ufw delete allow 8005

# Verify rules
sudo ufw status numbered
```

### 4.2 Enable HSTS and Security Headers
After confirming SSL works properly, uncomment the HSTS header in nginx config and add additional security headers:

```bash
# Edit the nginx config
sudo nano /opt/proyecto-sting/nginx/proyecto-sting.conf

# Uncomment or add these headers in the HTTPS server blocks:
# add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
# add_header X-Frame-Options "SAMEORIGIN" always;
# add_header X-Content-Type-Options "nosniff" always;
# add_header X-XSS-Protection "1; mode=block" always;
# add_header Referrer-Policy "no-referrer-when-downgrade" always;

# Reload nginx
sudo nginx -s reload
```

## Phase 5: Testing and Verification

### 5.1 Test All Endpoints
```bash
# Test main site
curl -I https://proyecto-sting.xyz

# Test www redirect
curl -I https://www.proyecto-sting.xyz

# Test API endpoint
curl -X POST https://api.proyecto-sting.xyz/route \
  -H "Content-Type: application/json" \
  -d '{"question":"test"}'

# Test SSL configuration
curl -sI https://proyecto-sting.xyz | grep -i strict
```

### 5.2 Verify SSL Grade
Visit https://www.ssllabs.com/ssltest/ and test your domain. You should get at least an A rating.

### 5.3 Check DNS Propagation
Visit https://www.whatsmydns.net/ and verify your domain resolves correctly worldwide.

## Troubleshooting

### DNS Not Resolving
- Wait up to 48 hours for full propagation
- Verify records in Porkbun dashboard
- Try flushing local DNS cache

### SSL Certificate Issues
```bash
# Check certificate details
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Application Not Loading
```bash
# Check Docker containers
docker-compose ps

# Check container logs
docker-compose logs frontend
docker-compose logs router

# Verify nginx is proxying correctly
curl -v http://localhost:80
```

### CORS Errors
- Ensure API subdomain certificate is valid
- Check browser console for specific CORS errors
- Verify nginx CORS headers are being sent

## Maintenance

### Monthly Tasks
- Monitor SSL certificate expiration
- Check for security updates
- Review nginx access logs for anomalies

### Commands Reference
```bash
# Renew SSL certificate manually
sudo certbot renew

# Restart all services
cd /opt/proyecto-sting && docker-compose restart

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Update and deploy
cd /opt/proyecto-sting && ./deploy-domain.sh
```

## Final Notes
- Keep your Porkbun account secure with 2FA
- Regularly backup your SSL certificates
- Monitor your domain expiration date
- Consider setting up monitoring with UptimeRobot or similar