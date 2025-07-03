#!/usr/bin/env python3
import asyncio
import httpx
import json

async def test():
    query = {"question": "¿Cuál es el límite actual 2025 para pagar Netflix desde Argentina?"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Direct to BCRA
        resp = await client.post("http://localhost:8002/answer", json=query)
        data = resp.json()
        
        print("Agent Response:")
        print(json.dumps(data.get("answer", {}).get("_search_metadata", {}), indent=2))
        
        # Send to auditor
        audit_req = {
            "user_question": query["question"],
            "agent_name": "bcra",
            "agent_response": data.get("answer", {})
        }
        
        audit_resp = await client.post("http://localhost:8005/audit", json=audit_req)
        audit_data = audit_resp.json()
        
        print("\nAuditor Metadata:")
        print(json.dumps(audit_data.get("metadata", {}), indent=2))
        
        # Format
        format_resp = await client.post("http://localhost:8005/format", json=audit_data)
        formatted = format_resp.json()
        
        print("\nFormatted Output (last 5 lines):")
        lines = formatted.get("markdown", "").split("\n")
        for line in lines[-5:]:
            print(line)

asyncio.run(test())