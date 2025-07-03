#!/usr/bin/env bash
# Health check script for all Bureaucracy Oracle services
# Tests both internal and external endpoints

set -euo pipefail

# Configuration
SERVICES=(
    "router:8001:https://router.up.railway.app"
    "bcra:8002:internal"
    "comex:8003:internal"
    "senasa:8004:internal"
    "auditor:8005:https://auditor.up.railway.app"
    "frontend:3000:https://frontend.up.railway.app"
)

# For local testing
LOCAL_MODE="${LOCAL_MODE:-false}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🏥 Bureaucracy Oracle - Health Check${NC}"
echo -e "Mode: $([ "$LOCAL_MODE" = "true" ] && echo "Local" || echo "Production")"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function to check health endpoint
check_health() {
    local service=$1
    local port=$2
    local url=$3
    local endpoint="/health"
    
    # Determine the full URL
    if [ "$LOCAL_MODE" = "true" ]; then
        full_url="http://localhost:${port}${endpoint}"
    elif [ "$url" = "internal" ]; then
        # Skip internal services in production mode
        echo -e "${YELLOW}⏭️  ${service} - internal service (skipped)${NC}"
        return 0
    else
        full_url="${url}${endpoint}"
    fi
    
    # Make health check request
    response=$(curl -sf -w "\n%{http_code}\n%{time_total}" "$full_url" 2>/dev/null || echo "ERROR\n000\n0")
    
    # Parse response
    http_code=$(echo "$response" | tail -2 | head -1)
    response_time=$(echo "$response" | tail -1)
    response_time_ms=$(echo "$response_time * 1000" | bc | cut -d. -f1)
    
    # Check status
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ ${service}:${port} - healthy (${response_time_ms}ms)${NC}"
        return 0
    else
        echo -e "${RED}❌ ${service}:${port} - unhealthy (HTTP ${http_code})${NC}"
        return 1
    fi
}

# Function to test a sample query
test_query() {
    local router_url
    if [ "$LOCAL_MODE" = "true" ]; then
        router_url="http://localhost:8001"
    else
        router_url="https://router.up.railway.app"
    fi
    
    echo -e "\n${YELLOW}🧪 Testing sample query...${NC}"
    
    # Sample query
    query_json='{
        "question": "¿Cuál es el límite para pagar Netflix desde Argentina?",
        "conversation_id": "health-check-test"
    }'
    
    # Make request
    start_time=$(date +%s%3N)
    response=$(curl -sf -X POST \
        -H "Content-Type: application/json" \
        -d "$query_json" \
        "${router_url}/query" \
        --max-time 30 2>/dev/null)
    end_time=$(date +%s%3N)
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        response_time=$((end_time - start_time))
        echo -e "${GREEN}✅ Query test passed (${response_time}ms)${NC}"
        
        # Check if response has expected structure
        if echo "$response" | jq -e '.agents_consulted' >/dev/null 2>&1; then
            agents=$(echo "$response" | jq -r '.agents_consulted[]' | tr '\n' ', ' | sed 's/,$//')
            echo "   Agents consulted: $agents"
        fi
        return 0
    else
        echo -e "${RED}❌ Query test failed${NC}"
        return 1
    fi
}

# Main health check loop
all_healthy=true
healthy_count=0
total_count=0

for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service port url <<< "$service_info"
    total_count=$((total_count + 1))
    
    if check_health "$service" "$port" "$url"; then
        healthy_count=$((healthy_count + 1))
    else
        all_healthy=false
    fi
done

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Status: ${healthy_count}/${total_count} services healthy"

# Test query if router is healthy
if [ "$LOCAL_MODE" = "true" ] || [ "$all_healthy" = true ]; then
    if test_query; then
        echo -e "\n${GREEN}✨ System fully operational!${NC}"
    else
        echo -e "\n${YELLOW}⚠️  Health checks passed but query test failed${NC}"
        all_healthy=false
    fi
fi

# Generate health report
report_file="logs/health-report-$(date +%Y%m%d-%H%M%S).json"
mkdir -p logs

cat > "$report_file" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "mode": "$([ "$LOCAL_MODE" = "true" ] && echo "local" || echo "production")",
  "services_healthy": $healthy_count,
  "services_total": $total_count,
  "all_healthy": $([ "$all_healthy" = "true" ] && echo "true" || echo "false"),
  "query_test": $([ "$all_healthy" = "true" ] && echo "true" || echo "false")
}
EOF

echo -e "\n📄 Report saved: $report_file"

# Exit based on health status
if [ "$all_healthy" = true ]; then
    exit 0
else
    exit 1
fi