#!/usr/bin/env python3
"""Test what search actually returns"""
import sys
sys.path.append('/Users/juanotero/Documents/GitHub/stingv2/agents')

from search_service import TavilySearchService
import asyncio
import os

async def test():
    # Set env vars
    os.environ["ENABLE_SEARCH"] = "true"
    os.environ["TAVILY_API_KEY"] = "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"
    
    service = TavilySearchService()
    
    # Test the search
    results = await service.search(
        "arancel importación notebooks Argentina 2025",
        "comex",
        max_results=3
    )
    
    print("Search Results:")
    print("-" * 60)
    
    # Show what format_for_prompt returns
    formatted = service.format_for_prompt(results)
    print(formatted)
    
    print("\n\nRaw results:")
    print("-" * 60)
    for source in results.get("sources", [])[:2]:
        print(f"\nTitle: {source.get('title')}")
        print(f"Content: {source.get('content', '')[:300]}...")

asyncio.run(test())