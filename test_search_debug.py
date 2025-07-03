#!/usr/bin/env python3
import httpx
import asyncio

async def test():
    # Test search directly
    query = "¿Cuál es el límite actual 2025 para pagar Netflix?"
    
    # Direct search test
    search_data = {
        "api_key": "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",
        "query": f"{query} BCRA Argentina límite pago servicios digitales 2025",
        "search_depth": "advanced",
        "max_results": 3,
        "include_answer": True,
        "include_raw_content": False,
        "include_domains": ["bcra.gob.ar", "boletinoficial.gob.ar", "infoleg.gob.ar"]
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post("https://api.tavily.com/search", json=search_data)
        print(f"Tavily Response Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Answer: {data.get('answer', 'No answer')[:200]}...")
            print(f"Results count: {len(data.get('results', []))}")
            for r in data.get('results', [])[:2]:
                print(f"- {r.get('url')}: {r.get('title')[:50]}...")

asyncio.run(test())