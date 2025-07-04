#!/bin/bash
# Health check script for Proyecto Sting
# Monitors services and restarts unhealthy containers

set -euo pipefail

# Change to app directory
APP_DIR="/opt/proyecto-sting"
cd "$APP_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Services to monitor
declare -A SERVICES=(
    ["router"]="8001"
    ["bcra"]="8002"
    ["comex"]="8003"
    ["senasa"]="8004"
    ["auditor"]="8005"
)

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check single service health
check_service() {
    local service=$1
    local port=${SERVICES[$service]}
    
    if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Restart unhealthy service
restart_service() {
    local service=$1
    log "Restarting $service..."
    docker-compose restart "$service"
    sleep 10
}

# Main monitoring loop
monitor_services() {
    log "Starting health monitoring..."
    
    while true; do
        for service in "${!SERVICES[@]}"; do
            if ! check_service "$service"; then
                log "❌ $service is unhealthy"
                restart_service "$service"
                
                # Check again after restart
                sleep 5
                if check_service "$service"; then
                    log "✅ $service recovered after restart"
                else
                    log "⚠️  $service still unhealthy after restart"
                fi
            fi
        done
        
        # Wait before next check cycle
        sleep 60
    done
}

# Run as daemon if -d flag provided
if [[ "${1:-}" == "-d" ]]; then
    log "Running in daemon mode..."
    monitor_services >> /var/log/proyecto-sting-health.log 2>&1 &
    echo $! > /var/run/proyecto-sting-health.pid
    echo -e "${GREEN}Health monitor started (PID: $!)${NC}"
    echo "Logs: /var/log/proyecto-sting-health.log"
else
    # Run in foreground
    monitor_services
fi