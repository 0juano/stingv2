#!/usr/bin/env python3
"""Test improved notebook tariff accuracy"""
import asyncio
import httpx
import json

async def test_notebook_tariff():
    # Same query that previously returned 15% instead of 16%
    query = {"question": "¿Cuál es el arancel actual para importar notebooks en 2025?"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Direct to COMEX
        print("Testing COMEX agent with improved prompt...")
        resp = await client.post("http://localhost:8003/answer", json=query)
        data = resp.json()
        
        answer = data.get("answer", {})
        
        print("\nAgent Response:")
        print(f"Response: {answer.get('Respuesta', 'No response')}")
        print(f"Arancel: {answer.get('ArancelExportacion', 'Not specified')}")
        print(f"NCM: {answer.get('NCM', 'Not specified')}")
        print(f"Search used: {answer.get('_search_metadata', {}).get('used', False)}")
        
        # Send to auditor
        audit_req = {
            "user_question": query["question"],
            "agent_name": "comex",
            "agent_response": answer
        }
        
        audit_resp = await client.post("http://localhost:8005/audit", json=audit_req)
        audit_data = audit_resp.json()
        
        # Format
        format_resp = await client.post("http://localhost:8005/format", json=audit_data)
        formatted = format_resp.json()
        
        print("\n" + "="*60)
        print("FORMATTED RESPONSE:")
        print("="*60)
        print(formatted.get("markdown", ""))
        
        # Check if it got the correct value
        markdown = formatted.get("markdown", "")
        if "16%" in markdown:
            print("\n✅ SUCCESS: Correct tariff value (16%) returned!")
        elif "15%" in markdown:
            print("\n❌ FAIL: Still returning incorrect value (15%)")
        else:
            print("\n⚠️  No specific percentage found in response")

asyncio.run(test_notebook_tariff())