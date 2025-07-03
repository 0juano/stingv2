#!/usr/bin/env python3
"""Test multi-agent search metadata"""
import asyncio
import httpx
import json

async def test():
    query = {"question": "¿Cómo importar productos farmacéuticos a Argentina?"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Get routing
        router_resp = await client.post("http://localhost:8001/route", json=query)
        routing = router_resp.json()
        agents = routing.get('route', {}).get('agents', [])
        print(f"Agents selected: {agents}")
        
        # Query each agent
        agent_responses = {}
        for agent in agents:
            port = {"bcra": 8002, "comex": 8003, "senasa": 8004}[agent]
            resp = await client.post(f"http://localhost:{port}/answer", json=query)
            agent_responses[agent] = resp.json()
            
            # Check search metadata
            answer = agent_responses[agent].get("answer", {})
            search_meta = answer.get("_search_metadata", {})
            print(f"\n{agent.upper()} search metadata: {search_meta}")
        
        # Send to multi-auditor
        audit_req = {
            "user_question": query["question"],
            "agent_responses": agent_responses,
            "primary_agent": agents[0] if agents else "comex"
        }
        
        audit_resp = await client.post("http://localhost:8005/audit-multi", json=audit_req)
        audit_data = audit_resp.json()
        
        # Check metadata
        metadata = audit_data.get("metadata", {})
        print(f"\nAuditor metadata:")
        print(f"  busquedas_web: {metadata.get('busquedas_web')}")
        print(f"  fuentes_consultadas: {metadata.get('fuentes_consultadas')}")

asyncio.run(test())