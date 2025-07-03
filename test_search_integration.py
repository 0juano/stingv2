#!/usr/bin/env python3
"""
Test search integration for all agents
"""
import asyncio
import httpx
import json
from datetime import datetime

# Test questions that should trigger search
TEST_QUESTIONS = {
    "bcra": "¿Cuál es el límite actual para pagar servicios digitales como Netflix desde Argentina?",
    "comex": "¿Qué arancel tiene la importación de notebooks en 2025?",
    "senasa": "¿Cuáles son los requisitos vigentes para exportar limones a Europa?"
}

async def test_agent(agent_name: str, question: str):
    """Test a single agent with search"""
    port = {
        "bcra": 8002,
        "comex": 8003,
        "senasa": 8004
    }[agent_name]
    
    url = f"http://localhost:{port}/answer"
    
    print(f"\n{'='*60}")
    print(f"Testing {agent_name.upper()} agent")
    print(f"Question: {question}")
    print(f"{'='*60}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            start_time = datetime.now()
            response = await client.post(url, json={"question": question})
            end_time = datetime.now()
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success in {(end_time - start_time).total_seconds():.2f}s")
                print(f"Model: {result.get('model', 'unknown')}")
                print(f"Cost: ${result.get('cost', 0):.4f}")
                
                answer = result.get('answer', {})
                if isinstance(answer, dict):
                    print("\nResponse structure:")
                    for key in answer.keys():
                        print(f"  - {key}")
                    
                    # Check if search was likely used
                    response_text = json.dumps(answer, ensure_ascii=False).lower()
                    search_indicators = ["fuente:", "según", "comunicación", "resolución", "decreto"]
                    if any(indicator in response_text for indicator in search_indicators):
                        print("  ✓ Search results appear to be integrated")
                else:
                    print(f"\nRaw answer: {answer}")
                
                return True
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

async def main():
    """Test all agents"""
    print("Testing Search Integration for All Agents")
    print("=" * 60)
    
    # First check if services are running
    print("\nChecking service health...")
    services_ok = True
    
    for agent, port in [("router", 8001), ("bcra", 8002), ("comex", 8003), ("senasa", 8004), ("auditor", 8005)]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"http://localhost:{port}/health")
                if response.status_code == 200:
                    print(f"  ✓ {agent} is healthy")
                else:
                    print(f"  ✗ {agent} returned {response.status_code}")
                    services_ok = False
        except:
            print(f"  ✗ {agent} is not responding")
            services_ok = False
    
    if not services_ok:
        print("\n⚠️  Some services are not running. Please run: make dev")
        return
    
    # Test each agent
    results = []
    for agent_name, question in TEST_QUESTIONS.items():
        success = await test_agent(agent_name, question)
        results.append((agent_name, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"{'='*60}")
    for agent, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{agent.upper()}: {status}")
    
    total_success = sum(1 for _, success in results if success)
    print(f"\nTotal: {total_success}/{len(results)} agents passed")

if __name__ == "__main__":
    asyncio.run(main())