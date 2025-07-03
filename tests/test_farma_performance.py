import requests
import time
import json

def test_farma_import():
    """Test the 'Importar Farma (TODOS)' query performance"""
    
    query = "¿Proceso completo para importar productos farmacéuticos?"
    
    # Start timing
    start_time = time.time()
    
    print(f"Testing query: {query}")
    print("-" * 60)
    
    # Step 1: Router
    router_start = time.time()
    router_response = requests.post(
        "http://localhost:8001/route",
        json={"question": query},
        timeout=60
    )
    router_time = time.time() - router_start
    
    print(f"✓ Router response time: {router_time:.2f}s")
    
    routing_result = router_response.json()
    print(f"  Full routing response: {json.dumps(routing_result, indent=2)}")
    
    # Get the decision object
    decision = routing_result.get('decision', {})
    agents_from_decision = decision.get('agents', [])
    print(f"  Agents to query: {agents_from_decision}")
    
    # Step 2: Query agents in parallel (simulating what the frontend does)
    agents_to_query = agents_from_decision
    
    if len(agents_to_query) > 1:
        print(f"\nQuerying {len(agents_to_query)} agents in parallel...")
        
        # In reality, the frontend queries these in parallel
        # For this test, we'll query them sequentially to measure each
        agent_responses = {}
        
        for agent in agents_to_query:
            agent_start = time.time()
            try:
                agent_response = requests.post(
                    f"http://localhost:{8002 if agent == 'bcra' else 8003 if agent == 'comex' else 8004}/answer",
                    json={"question": query},
                    timeout=60
                )
                agent_time = time.time() - agent_start
                agent_responses[agent] = agent_response.json()
                print(f"  ✓ {agent.upper()} response time: {agent_time:.2f}s")
            except Exception as e:
                print(f"  ✗ {agent.upper()} error: {str(e)}")
        
        # Step 3: Audit multi-agent responses
        audit_start = time.time()
        audit_response = requests.post(
            "http://localhost:8005/audit-multi",
            json={
                "question": query,
                "agents": agents_to_query,
                "responses": agent_responses
            },
            timeout=90
        )
        audit_time = time.time() - audit_start
        print(f"\n✓ Multi-agent audit time: {audit_time:.2f}s")
        
    else:
        print(f"\nQuerying single agent: {agents_to_query[0] if agents_to_query else 'None'}")
    
    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"TOTAL TIME: {total_time:.2f}s")
    
    if total_time > 30:
        print("\n⚠️  Query took longer than 30 seconds!")
        print("Possible issues:")
        print("- Multiple agents being queried (3x API calls)")
        print("- Complex multi-agent audit integration")
        print("- OpenRouter API latency")
        print("- No caching mechanism")

if __name__ == "__main__":
    test_farma_import()