#!/usr/bin/env python3
"""Test search functionality across all agents"""
import asyncio
import httpx
import json

async def test_agent_search(agent_name: str, port: int, question: str):
    """Test search for a specific agent"""
    print(f"\n{'='*60}")
    print(f"Testing {agent_name.upper()} agent on port {port}")
    print(f"Question: {question}")
    print('-'*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(f"http://localhost:{port}/answer", json={"question": question})
            data = resp.json()
            
            answer = data.get("answer", {})
            search_meta = answer.get("_search_metadata", {})
            
            print(f"Search used: {search_meta.get('used', False)}")
            print(f"Search count: {search_meta.get('count', 0)}")
            print(f"Cost: ${data.get('cost', 0):.4f}")
            
            if search_meta.get('used'):
                print(f"Sources: {search_meta.get('sources_consulted', [])[:3]}")
            
            return True
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return False

async def main():
    """Test all agents"""
    tests = [
        ("bcra", 8002, "¿Cuál es el límite para pagos con tarjeta en el exterior?"),
        ("comex", 8003, "¿Cuál es el arancel para importar notebooks?"),
        ("senasa", 8004, "¿Qué requisitos hay para exportar carne a China?")
    ]
    
    results = []
    for agent_name, port, question in tests:
        success = await test_agent_search(agent_name, port, question)
        results.append((agent_name, success))
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    for agent_name, success in results:
        status = "✅ Working" if success else "❌ Failed"
        print(f"{agent_name.upper()}: {status}")

if __name__ == "__main__":
    asyncio.run(main())