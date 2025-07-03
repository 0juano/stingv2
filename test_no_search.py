#!/usr/bin/env python3
"""Test that no search indicator appears"""
import asyncio
import httpx

async def test():
    query = {"question": "¿Qué es el BCRA?"}  # Simple query that shouldn't trigger search
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Direct to BCRA
        resp = await client.post("http://localhost:8002/answer", json=query)
        data = resp.json()
        
        # Send to auditor
        audit_req = {
            "user_question": query["question"],
            "agent_name": "bcra",
            "agent_response": data.get("answer", {})
        }
        
        audit_resp = await client.post("http://localhost:8005/audit", json=audit_req)
        audit_data = audit_resp.json()
        
        # Format
        format_resp = await client.post("http://localhost:8005/format", json=audit_data)
        formatted = format_resp.json()
        
        # Show full response to debug
        print("Full response:")
        print(formatted.get("markdown", ""))

asyncio.run(test())