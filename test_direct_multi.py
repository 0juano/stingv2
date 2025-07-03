#!/usr/bin/env python3
"""Test multi-agent directly"""
import asyncio
import httpx
import json

async def test():
    query = {"question": "¿Cómo importar productos farmacéuticos a Argentina?"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Manually test each agent
        agents = ["senasa", "comex", "bcra"]
        agent_responses = {}
        
        for agent in agents:
            port = {"bcra": 8002, "comex": 8003, "senasa": 8004}[agent]
            print(f"\nTesting {agent.upper()}...")
            resp = await client.post(f"http://localhost:{port}/answer", json=query)
            agent_responses[agent] = resp.json()
            
            # Check search metadata
            answer = agent_responses[agent].get("answer", {})
            search_meta = answer.get("_search_metadata", {})
            print(f"  Search metadata: {search_meta}")
        
        # Send to multi-auditor
        audit_req = {
            "user_question": query["question"],
            "agent_responses": agent_responses,
            "primary_agent": "senasa"
        }
        
        print("\nSending to auditor...")
        audit_resp = await client.post("http://localhost:8005/audit-multi", json=audit_req)
        audit_data = audit_resp.json()
        
        # Check metadata
        metadata = audit_data.get("metadata", {})
        print(f"\nAuditor metadata:")
        print(f"  busquedas_web: {metadata.get('busquedas_web')}")
        print(f"  agentes_consultados: {metadata.get('agentes_consultados')}")
        
        # Format
        format_resp = await client.post("http://localhost:8005/format", json=audit_data)
        formatted = format_resp.json()
        
        # Show last lines
        print("\nLast lines of formatted response:")
        lines = formatted.get("markdown", "").split("\n")
        for line in lines[-10:]:
            if line.strip():
                print(f"  {line}")

asyncio.run(test())