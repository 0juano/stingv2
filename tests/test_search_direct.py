#!/usr/bin/env python3
"""Direct test of search functionality"""
import os
import asyncio

# Set environment
os.environ["ENABLE_SEARCH"] = "true"
os.environ["TAVILY_API_KEY"] = "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"

# Import after setting env
from agents.search_service import get_search_service

async def test_search():
    service = get_search_service()
    
    print(f"Search enabled: {service.enabled}")
    print(f"API key present: {bool(service.api_key)}")
    
    # Test if search is needed
    test_queries = [
        ("¿Qué arancel tiene la importación de notebooks?", "comex"),
        ("¿Qué es el BCRA?", "bcra"),
        ("¿Cuál es el límite actual para Netflix?", "bcra")
    ]
    
    for query, agent in test_queries:
        needs = service.needs_search(query, agent)
        print(f"\n'{query}' needs search: {needs}")
        
        if needs:
            print("Performing search...")
            results = await service.search(query, agent)
            if results.get("error"):
                print(f"Error: {results['message']}")
            else:
                print(f"Found {len(results.get('sources', []))} sources")
                if results.get('key_facts'):
                    print(f"Key facts: {results['key_facts']}")

if __name__ == "__main__":
    asyncio.run(test_search())