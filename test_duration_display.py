import requests
import time

def test_duration_tracking():
    """Test that duration is properly tracked and can be displayed"""
    
    # Simple BCRA query that should be fast
    query = "¿Qué es el CEPO cambiario?"
    
    print(f"Testing duration tracking with query: {query}")
    print("-" * 60)
    
    # Simulate the orchestrator flow
    start_time = time.time()
    
    # Step 1: Router
    router_response = requests.post(
        "http://localhost:8001/route",
        json={"question": query},
        timeout=10
    )
    
    routing_result = router_response.json()
    decision = routing_result.get('decision', {})
    agents = decision.get('agents', [])
    
    if not agents:
        print("No agents returned by router")
        return
    
    # Step 2: Single agent (BCRA should handle this)
    agent = agents[0]
    agent_port = 8002 if agent == 'bcra' else 8003 if agent == 'comex' else 8004
    
    agent_response = requests.post(
        f"http://localhost:{agent_port}/answer",
        json={"question": query},
        timeout=35
    )
    
    # Step 3: Audit
    audit_response = requests.post(
        "http://localhost:8005/audit",
        json={
            "user_question": query,
            "agent_response": agent_response.json().get("answer", {}),
            "agent_name": agent
        },
        timeout=30
    )
    
    # Step 4: Format
    format_response = requests.post(
        "http://localhost:8005/format",
        json=audit_response.json(),
        timeout=15
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✓ Query completed successfully")
    print(f"Duration: {duration:.1f}s")
    print(f"Agent consulted: {agent.upper()}")
    
    # Calculate costs
    total_cost = (
        routing_result.get('cost', 0) +
        agent_response.json().get('cost', 0) +
        audit_response.json().get('cost', 0)
    )
    
    print(f"Total cost: ${total_cost:.4f}")
    print("\nNow the frontend should display:")
    print(f"💰 Cost: ${total_cost:.4f}")
    print(f"⏱️ Time: {duration:.1f}s")

if __name__ == "__main__":
    test_duration_tracking()