#!/usr/bin/env python3
"""Test quick search functionality"""
import asyncio
import httpx
import json

async def test_quick_search():
    """Test a simple query with quick search"""
    question = "¿Qué es COMEX?"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Direct to COMEX
        resp = await client.post("http://localhost:8003/answer", json={"question": question})
        data = resp.json()
        
        print(f"Question: {question}")
        print(f"Cost: ${data.get('cost', 0):.4f}")
        
        answer = data.get("answer", {})
        search_meta = answer.get("_search_metadata", {})
        
        print(f"Search used: {search_meta.get('used', False)}")
        print(f"Search count: {search_meta.get('count', 0)}")
        
        if search_meta.get('used'):
            print(f"Sources: {search_meta.get('sources_consulted', [])}")
        
        # Send to auditor
        audit_req = {
            "user_question": question,
            "agent_name": "comex",
            "agent_response": answer
        }
        
        audit_resp = await client.post("http://localhost:8005/audit", json=audit_req)
        audit_data = audit_resp.json()
        
        format_resp = await client.post("http://localhost:8005/format", json=audit_data)
        formatted = format_resp.json()
        
        print("\nFormatted response:")
        print(formatted.get("markdown", ""))

if __name__ == "__main__":
    asyncio.run(test_quick_search())