#!/usr/bin/env python3
"""
Test search metadata tracking
"""
import asyncio
import httpx
import json

async def test_single_agent():
    """Test single agent with search metadata"""
    print("Testing single agent with search...")
    
    # Query that should trigger search
    query = {
        "question": "¿Cuál es el arancel actual para importar notebooks en 2025?"
    }
    
    # Send to router
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Get routing
        router_resp = await client.post("http://localhost:8001/route", json=query)
        routing = router_resp.json()
        print(f"Router selected: {routing.get('route', {}).get('agents', [])}")
        
        # Get agent response
        agent_resp = await client.post(
            f"http://localhost:{8003}/answer",  # COMEX port
            json=query
        )
        agent_data = agent_resp.json()
        
        # Check for search metadata
        answer = agent_data.get("answer", {})
        search_meta = answer.get("_search_metadata", {})
        print(f"\nSearch metadata found: {search_meta}")
        
        # Send to auditor
        audit_req = {
            "user_question": query["question"],
            "agent_name": "comex",
            "agent_response": answer
        }
        
        audit_resp = await client.post(
            "http://localhost:8005/audit",
            json=audit_req
        )
        audit_data = audit_resp.json()
        
        # Check auditor metadata
        print(f"\nAuditor metadata: {audit_data.get('metadata', {})}")
        
        # Get formatted response
        format_resp = await client.post(
            "http://localhost:8005/format",
            json=audit_data
        )
        formatted = format_resp.json()
        
        print("\n" + "="*60)
        print("FORMATTED RESPONSE:")
        print("="*60)
        print(formatted.get("markdown", "No markdown found"))

async def test_multi_agent():
    """Test multi-agent with aggregated search metadata"""
    print("\n\nTesting multi-agent with search...")
    
    # Query that needs multiple agents
    query = {
        "question": "¿Cómo exportar vino a Brasil? Necesito saber requisitos aduaneros y sanitarios actuales"
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Get routing
        router_resp = await client.post("http://localhost:8001/route", json=query)
        routing = router_resp.json()
        agents = routing.get('route', {}).get('agents', [])
        print(f"Router selected agents: {agents}")
        
        # Query multiple agents
        agent_responses = {}
        for agent in agents:
            port = {"bcra": 8002, "comex": 8003, "senasa": 8004}[agent]
            resp = await client.post(f"http://localhost:{port}/answer", json=query)
            agent_responses[agent] = resp.json()
            
            # Show search metadata for each agent
            answer = agent_responses[agent].get("answer", {})
            search_meta = answer.get("_search_metadata", {})
            print(f"\n{agent.upper()} search metadata: {search_meta}")
        
        # Send to multi-auditor
        audit_req = {
            "user_question": query["question"],
            "agent_responses": agent_responses,
            "primary_agent": agents[0] if agents else "comex"
        }
        
        audit_resp = await client.post(
            "http://localhost:8005/audit-multi",
            json=audit_req
        )
        audit_data = audit_resp.json()
        
        # Check aggregated metadata
        print(f"\nAggregated auditor metadata: {audit_data.get('metadata', {})}")
        
        # Get formatted response
        format_resp = await client.post(
            "http://localhost:8005/format",
            json=audit_data
        )
        formatted = format_resp.json()
        
        print("\n" + "="*60)
        print("FORMATTED MULTI-AGENT RESPONSE:")
        print("="*60)
        print(formatted.get("markdown", "No markdown found"))

async def main():
    """Run all tests"""
    await test_single_agent()
    await test_multi_agent()

if __name__ == "__main__":
    asyncio.run(main())