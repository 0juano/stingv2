#!/usr/bin/env python3
"""
Railway cost monitoring script
Tracks resource usage and estimates monthly costs
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Railway API configuration
RAILWAY_API_URL = "https://api.railway.app/graphql/v2"
RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN")
PROJECT_ID = os.getenv("RAILWAY_PROJECT_ID")
MONTHLY_BUDGET_USD = float(os.getenv("MONTHLY_BUDGET_USD", "20"))

# Service configuration
SERVICES = ["router", "bcra", "comex", "senasa", "auditor", "frontend"]

# Pricing (Railway Hobby Plan)
PRICING = {
    "cpu_per_vcpu_hour": 0.000463,  # $0.000463 per vCPU per hour
    "memory_per_gb_hour": 0.000231,  # $0.000231 per GB per hour
    "network_egress_per_gb": 0.10,   # $0.10 per GB egress
}


def get_service_metrics(service_name: str, hours: int = 24) -> Optional[Dict]:
    """Fetch metrics for a specific service from Railway API"""
    if not RAILWAY_TOKEN:
        print(f"❌ Missing RAILWAY_TOKEN environment variable")
        return None
    
    query = """
    query GetServiceMetrics($projectId: String!, $serviceName: String!, $from: DateTime!, $to: DateTime!) {
        project(id: $projectId) {
            services(filter: {name: $serviceName}) {
                edges {
                    node {
                        name
                        metrics(from: $from, to: $to) {
                            cpu {
                                average
                                max
                            }
                            memory {
                                average
                                max
                            }
                            networkEgress {
                                total
                            }
                        }
                    }
                }
            }
        }
    }
    """
    
    now = datetime.utcnow()
    from_time = now - timedelta(hours=hours)
    
    variables = {
        "projectId": PROJECT_ID,
        "serviceName": service_name,
        "from": from_time.isoformat() + "Z",
        "to": now.isoformat() + "Z"
    }
    
    headers = {
        "Authorization": f"Bearer {RAILWAY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            RAILWAY_API_URL,
            json={"query": query, "variables": variables},
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        if "errors" in data:
            print(f"❌ GraphQL errors: {data['errors']}")
            return None
            
        services = data.get("data", {}).get("project", {}).get("services", {}).get("edges", [])
        if services:
            return services[0]["node"]["metrics"]
        return None
        
    except Exception as e:
        print(f"❌ Error fetching metrics for {service_name}: {e}")
        return None


def calculate_cost(metrics: Dict, hours: int) -> Dict[str, float]:
    """Calculate cost based on metrics"""
    # CPU cost (assuming 0.5 vCPU allocation)
    cpu_hours = hours * 0.5  # 0.5 vCPU
    cpu_cost = cpu_hours * PRICING["cpu_per_vcpu_hour"]
    
    # Memory cost (assuming 512MB = 0.5GB)
    memory_hours = hours * 0.5  # 0.5 GB
    memory_cost = memory_hours * PRICING["memory_per_gb_hour"]
    
    # Network egress cost
    network_gb = metrics.get("networkEgress", {}).get("total", 0) / (1024 ** 3)  # Convert to GB
    network_cost = network_gb * PRICING["network_egress_per_gb"]
    
    return {
        "cpu": cpu_cost,
        "memory": memory_cost,
        "network": network_cost,
        "total": cpu_cost + memory_cost + network_cost
    }


def main():
    """Main monitoring function"""
    print("🚂 Railway Cost Monitor - Bureaucracy Oracle")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💰 Monthly Budget: ${MONTHLY_BUDGET_USD}")
    print("=" * 50)
    
    if not PROJECT_ID:
        print("❌ Missing RAILWAY_PROJECT_ID environment variable")
        print("   Set it in your .env file or Railway dashboard")
        return
    
    total_daily_cost = 0
    service_costs = {}
    
    # Fetch metrics for each service
    for service in SERVICES:
        print(f"\n📊 Analyzing {service}...")
        
        # Get 24-hour metrics
        metrics = get_service_metrics(service, hours=24)
        
        if metrics:
            # Calculate daily cost
            daily_cost = calculate_cost(metrics, 24)
            service_costs[service] = daily_cost
            total_daily_cost += daily_cost["total"]
            
            print(f"  CPU cost:     ${daily_cost['cpu']:.4f}/day")
            print(f"  Memory cost:  ${daily_cost['memory']:.4f}/day")
            print(f"  Network cost: ${daily_cost['network']:.4f}/day")
            print(f"  Daily total:  ${daily_cost['total']:.4f}")
        else:
            # Estimate based on resource allocation
            estimated_daily = (24 * 0.5 * PRICING["cpu_per_vcpu_hour"] + 
                             24 * 0.5 * PRICING["memory_per_gb_hour"])
            service_costs[service] = {"total": estimated_daily, "estimated": True}
            total_daily_cost += estimated_daily
            print(f"  ⚠️  Using estimated cost: ${estimated_daily:.4f}/day")
    
    # Calculate projections
    print("\n" + "=" * 50)
    print("💸 Cost Summary")
    print("=" * 50)
    
    monthly_projection = total_daily_cost * 30
    weekly_projection = total_daily_cost * 7
    
    print(f"Daily total:    ${total_daily_cost:.2f}")
    print(f"Weekly total:   ${weekly_projection:.2f}")
    print(f"Monthly total:  ${monthly_projection:.2f}")
    
    # Budget analysis
    print(f"\n📊 Budget Analysis")
    budget_usage = (monthly_projection / MONTHLY_BUDGET_USD) * 100
    remaining_budget = MONTHLY_BUDGET_USD - monthly_projection
    
    if budget_usage <= 80:
        status = "✅ Within budget"
        color = "green"
    elif budget_usage <= 100:
        status = "⚠️  Approaching limit"
        color = "yellow"
    else:
        status = "❌ Over budget!"
        color = "red"
    
    print(f"Budget usage:   {budget_usage:.1f}% {status}")
    print(f"Remaining:      ${remaining_budget:.2f}")
    
    # Save report
    report_file = f"logs/cost-report-{datetime.now().strftime('%Y%m%d')}.json"
    os.makedirs("logs", exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "project_id": PROJECT_ID,
        "services": service_costs,
        "totals": {
            "daily": total_daily_cost,
            "weekly": weekly_projection,
            "monthly": monthly_projection
        },
        "budget": {
            "limit": MONTHLY_BUDGET_USD,
            "usage_percent": budget_usage,
            "remaining": remaining_budget,
            "status": status
        }
    }
    
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved: {report_file}")
    
    # Alert if over budget
    if budget_usage > 90:
        print("\n🚨 ALERT: Cost approaching budget limit!")
        print("   Consider enabling auto-sleep or reducing resources")
    
    # Exit code based on budget
    exit(0 if budget_usage <= 100 else 1)


if __name__ == "__main__":
    main()