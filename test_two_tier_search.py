#!/usr/bin/env python3
"""Test two-tier search system"""
import asyncio
import httpx
import json

async def test_query(question: str, expected_search: str):
    """Test a single query and check search behavior"""
    print(f"\n{'='*60}")
    print(f"Query: {question}")
    print(f"Expected: {expected_search}")
    print('-'*60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Direct to COMEX for testing
        resp = await client.post("http://localhost:8003/answer", json={"question": question})
        data = resp.json()
        
        answer = data.get("answer", {})
        search_meta = answer.get("_search_metadata", {})
        
        print(f"Search used: {search_meta.get('used', False)}")
        print(f"Search count: {search_meta.get('count', 0)}")
        print(f"Cost: ${data.get('cost', 0):.4f}")
        
        # Send to auditor and format
        audit_req = {
            "user_question": question,
            "agent_name": "comex",
            "agent_response": answer
        }
        
        audit_resp = await client.post("http://localhost:8005/audit", json=audit_req)
        audit_data = audit_resp.json()
        
        format_resp = await client.post("http://localhost:8005/format", json=audit_data)
        formatted = format_resp.json()
        
        # Extract search line
        lines = formatted.get("markdown", "").split("\n")
        for line in lines:
            if "🔍" in line:
                print(f"Display: {line.strip()}")
                break
        
        # Check if it matches expectation
        actual_count = search_meta.get('count', 0)
        if expected_search == "none" and actual_count == 0:
            print("✅ Correct: No search performed")
        elif expected_search == "quick" and actual_count == 1:
            print("✅ Correct: Quick search only")
        elif expected_search == "full" and actual_count == 2:
            print("✅ Correct: Full search (quick + advanced)")
        else:
            print(f"❌ Mismatch: Expected {expected_search}, got {actual_count} searches")

async def main():
    """Test various query types"""
    print("Testing Two-Tier Search System")
    
    test_cases = [
        # (question, expected_search_type)
        ("¿Qué es COMEX?", "quick"),  # Simple definition - quick search
        ("¿Cuál es el arancel para importar notebooks?", "full"),  # Has "arancel" + "import" - full search
        ("¿Cómo exportar vino a Brasil?", "full"),  # Has "export" - full search
        ("¿Qué significa NCM?", "quick"),  # Simple question - quick search
        ("¿Cuál es el límite actual para importar autos?", "full"),  # Has "límite" + "actual" + "import" - full search
        ("requisitos para certificado de origen", "full"),  # Has "requisitos" + "certificado" - full search
    ]
    
    for question, expected in test_cases:
        await test_query(question, expected)
    
    print(f"\n{'='*60}")
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(main())