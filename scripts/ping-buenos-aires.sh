#!/usr/bin/env bash
# Test latency from Buenos Aires to Railway services
# Measures RTT and reports p95 latency

set -euo pipefail

# Configuration
ROUTER_URL="${ROUTER_URL:-https://router.up.railway.app}"
ITERATIONS="${ITERATIONS:-100}"
TARGET_RTT_MS=170
TARGET_P95_MS=500

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🌐 Testing latency to Bureaucracy Oracle from Buenos Aires${NC}"
echo "Target: $ROUTER_URL"
echo "Iterations: $ITERATIONS"
echo ""

# Array to store response times
declare -a response_times=()

# Function to measure single request
measure_rtt() {
    local start_ms=$(date +%s%3N)
    
    # Make request with timeout
    if curl -sf -w "" "$ROUTER_URL/health" -o /dev/null --max-time 5; then
        local end_ms=$(date +%s%3N)
        local rtt=$((end_ms - start_ms))
        echo -n "."
        return $rtt
    else
        echo -n "X"
        return 9999  # Timeout/error
    fi
}

# Run measurements
echo -n "Measuring RTT: "
for i in $(seq 1 $ITERATIONS); do
    measure_rtt
    response_times+=($?)
    
    # Add newline every 50 iterations
    if [ $((i % 50)) -eq 0 ]; then
        echo ""
        echo -n "               "
    fi
done
echo ""

# Sort array for percentile calculation
IFS=$'\n' sorted=($(sort -n <<<"${response_times[*]}"))
unset IFS

# Calculate statistics
total=0
valid_count=0
for time in "${sorted[@]}"; do
    if [ "$time" -lt 9999 ]; then
        total=$((total + time))
        valid_count=$((valid_count + 1))
    fi
done

if [ "$valid_count" -eq 0 ]; then
    echo -e "${RED}Error: All requests failed!${NC}"
    exit 1
fi

# Calculate metrics
avg_rtt=$((total / valid_count))
min_rtt=${sorted[0]}
max_rtt=${sorted[$valid_count-1]}
p50_index=$((valid_count * 50 / 100))
p95_index=$((valid_count * 95 / 100))
p99_index=$((valid_count * 99 / 100))
p50_rtt=${sorted[$p50_index]}
p95_rtt=${sorted[$p95_index]}
p99_rtt=${sorted[$p99_index]}

# Display results
echo ""
echo -e "${YELLOW}📊 Latency Statistics (ms)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "Min:     %4d ms\n" "$min_rtt"
printf "Average: %4d ms %s\n" "$avg_rtt" \
    "$([ $avg_rtt -le $TARGET_RTT_MS ] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗ (target: <${TARGET_RTT_MS}ms)${NC}")"
printf "Median:  %4d ms\n" "$p50_rtt"
printf "p95:     %4d ms %s\n" "$p95_rtt" \
    "$([ $p95_rtt -le $TARGET_P95_MS ] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗ (target: <${TARGET_P95_MS}ms)${NC}")"
printf "p99:     %4d ms\n" "$p99_rtt"
printf "Max:     %4d ms\n" "$max_rtt"
echo ""
printf "Success: %d/%d (%.1f%%)\n" "$valid_count" "$ITERATIONS" \
    "$(echo "scale=1; $valid_count * 100 / $ITERATIONS" | bc)"

# Log results for monitoring
LOG_FILE="logs/latency-$(date +%Y%m%d-%H%M%S).json"
mkdir -p logs
cat > "$LOG_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "location": "Buenos Aires",
  "target": "$ROUTER_URL",
  "iterations": $ITERATIONS,
  "metrics": {
    "min_ms": $min_rtt,
    "avg_ms": $avg_rtt,
    "p50_ms": $p50_rtt,
    "p95_ms": $p95_rtt,
    "p99_ms": $p99_rtt,
    "max_ms": $max_rtt,
    "success_rate": $(echo "scale=2; $valid_count / $ITERATIONS" | bc)
  },
  "targets": {
    "avg_ms": $TARGET_RTT_MS,
    "p95_ms": $TARGET_P95_MS
  },
  "passed": $([ $avg_rtt -le $TARGET_RTT_MS ] && [ $p95_rtt -le $TARGET_P95_MS ] && echo "true" || echo "false")
}
EOF

echo ""
echo -e "${GREEN}Results saved to: $LOG_FILE${NC}"

# Exit code based on targets
if [ $avg_rtt -le $TARGET_RTT_MS ] && [ $p95_rtt -le $TARGET_P95_MS ]; then
    echo -e "${GREEN}✅ All latency targets met!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some latency targets not met${NC}"
    exit 1
fi