#!/usr/bin/env python3
"""Verify notebook import tariff information"""
import httpx
import asyncio
import json

async def verify_tariff():
    # Search for actual notebook import tariff
    search_data = {
        "api_key": "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",
        "query": "arancel importación notebooks NCM 8471.30.00 Argentina 2024 porcentaje",
        "search_depth": "advanced",
        "max_results": 5,
        "include_answer": True,
        "include_raw_content": False,
        "include_domains": ["afip.gob.ar", "tarifar.com", "argentina.gob.ar", "boletinoficial.gob.ar"]
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post("https://api.tavily.com/search", json=search_data)
        
        if resp.status_code == 200:
            data = resp.json()
            print("Search Answer:")
            print("-" * 60)
            print(data.get('answer', 'No answer'))
            print("\nTop Results:")
            print("-" * 60)
            
            for i, result in enumerate(data.get('results', [])[:3], 1):
                print(f"\n{i}. {result.get('title')}")
                print(f"   URL: {result.get('url')}")
                print(f"   Content: {result.get('content', '')[:200]}...")
                
            # Also check the resolutions mentioned
            print("\n\nVerifying mentioned resolutions:")
            print("-" * 60)
            
            # Search for Resolution 5542/2024
            search_res = {
                "api_key": "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",
                "query": "Resolución General 5542/2024 AFIP notebooks",
                "search_depth": "basic",
                "max_results": 2
            }
            
            resp2 = await client.post("https://api.tavily.com/search", json=search_res)
            if resp2.status_code == 200:
                data2 = resp2.json()
                for result in data2.get('results', [])[:1]:
                    print(f"Resolution 5542/2024: {result.get('title', 'Not found')}")

asyncio.run(verify_tariff())