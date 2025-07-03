"""
Tavily Search Service for Real-time Information Retrieval
"""
import os
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import hashlib
import asyncio
from search_config import AGENT_SEARCH_CONFIG, TEMPORAL_TRIGGERS, CACHE_DURATIONS


class SearchCache:
    """Simple in-memory cache for search results"""
    def __init__(self):
        self.cache = {}
    
    def get_key(self, query: str, agent_type: str) -> str:
        return hashlib.md5(f"{query}:{agent_type}".encode()).hexdigest()
    
    def get(self, query: str, agent_type: str) -> Optional[Dict]:
        key = self.get_key(query, agent_type)
        if key not in self.cache:
            return None
            
        cached = self.cache[key]
        if self._is_valid(cached):
            return cached["results"]
        
        del self.cache[key]
        return None
    
    def set(self, query: str, agent_type: str, results: Dict):
        key = self.get_key(query, agent_type)
        self.cache[key] = {
            "query": query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _is_valid(self, cached_data: Dict) -> bool:
        cached_time = datetime.fromisoformat(cached_data.get("timestamp", ""))
        query = cached_data.get("query", "").lower()
        
        # Determine cache duration based on query type
        if any(term in query for term in ["cotización", "dólar", "tipo de cambio"]):
            duration = timedelta(hours=CACHE_DURATIONS["exchange_rate"])
        else:
            duration = timedelta(hours=CACHE_DURATIONS["regulation"])
        
        return datetime.now() - cached_time < duration


class TavilySearchService:
    """Modular search service using Tavily API"""
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.enabled = os.getenv("ENABLE_SEARCH", "false").lower() == "true"
        self.base_url = "https://api.tavily.com"
        self.cache = SearchCache()
        
        if self.enabled and not self.api_key:
            raise ValueError("Search enabled but TAVILY_API_KEY not found")
    
    def needs_search(self, question: str, agent_type: str) -> bool:
        """Check if search is needed based on triggers"""
        if not self.enabled:
            return False
        
        question_lower = question.lower()
        
        # Check temporal triggers
        has_temporal = any(t in question_lower for t in TEMPORAL_TRIGGERS)
        
        # Check agent-specific triggers
        agent_triggers = AGENT_SEARCH_CONFIG.get(agent_type, {}).get("triggers", [])
        has_agent_trigger = any(t in question_lower for t in agent_triggers)
        
        return has_temporal or has_agent_trigger
    
    async def search(self, query: str, agent_type: str, max_results: int = 5) -> Dict[str, Any]:
        """Perform search with caching and agent optimization"""
        if not self.enabled:
            return {"error": True, "message": "Search disabled", "results": []}
        
        # Check cache
        cached = self.cache.get(query, agent_type)
        if cached:
            return cached
        
        # Build enhanced query
        config = AGENT_SEARCH_CONFIG.get(agent_type, {})
        enhanced_query = self._build_query(query, config)
        
        # Execute search
        try:
            results = await self._execute_search(enhanced_query, config, max_results)
            processed = self._process_results(results, agent_type)
            
            # Cache results
            self.cache.set(query, agent_type, processed)
            return processed
            
        except Exception as e:
            return {"error": True, "message": str(e), "results": []}
    
    def _build_query(self, query: str, config: Dict) -> str:
        """Build optimized search query"""
        current_year = datetime.now().year
        parts = [
            query,
            " ".join(config.get("keywords", [])),
            str(current_year),
            str(current_year - 1)
        ]
        
        enhanced = " ".join(parts)
        if config.get("search_suffix"):
            enhanced = f"{enhanced} {config['search_suffix']}"
        
        return enhanced
    
    async def _execute_search(self, query: str, config: Dict, max_results: int) -> Dict:
        """Execute Tavily API search"""
        params = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": max_results,
            "include_answer": True,
            "include_raw_content": False,
            "include_domains": config.get("domains", []),
            "exclude_domains": []
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.base_url}/search", json=params)
            response.raise_for_status()
            return response.json()
    
    def _process_results(self, raw_results: Dict, agent_type: str) -> Dict[str, Any]:
        """Process and extract key information"""
        import re
        
        results = raw_results.get("results", [])[:5]
        answer = raw_results.get("answer", "")
        
        processed = {
            "summary": answer,
            "sources": [],
            "key_facts": [],
            "last_updated": datetime.now().isoformat()
        }
        
        for result in results:
            source = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:500],
                "score": result.get("score", 0)
            }
            processed["sources"].append(source)
            
            # Extract agent-specific facts
            content = source["content"].lower()
            
            if agent_type == "comex" and "arancel" in content:
                percentages = re.findall(r'\d+(?:\.\d+)?%', source["content"])
                if percentages:
                    processed["key_facts"].append(f"Aranceles: {', '.join(set(percentages))}")
            
            elif agent_type == "bcra":
                amounts = re.findall(r'(?:USD?\s*)?(?:\$\s*)?\d+(?:\.\d+)?', source["content"])
                if amounts and len(amounts) <= 5:
                    processed["key_facts"].append(f"Montos: {', '.join(amounts[:3])}")
        
        return processed
    
    def format_for_prompt(self, search_results: Dict[str, Any]) -> str:
        """Format results for LLM prompt inclusion"""
        if search_results.get("error") or not search_results.get("sources"):
            return ""
        
        lines = ["=== INFORMACIÓN ACTUALIZADA ===\n"]
        
        if search_results.get("summary"):
            lines.append(f"RESUMEN: {search_results['summary']}\n")
        
        if search_results.get("key_facts"):
            lines.append("DATOS CLAVE:")
            lines.extend(f"• {fact}" for fact in search_results["key_facts"])
            lines.append("")
        
        if search_results.get("sources"):
            lines.append("FUENTES:")
            for i, source in enumerate(search_results["sources"][:3], 1):
                lines.append(f"{i}. {source['title']}")
                lines.append(f"   {source['url']}")
                lines.append(f"   {source['content'][:150]}...\n")
        
        lines.append(f"Actualizado: {search_results.get('last_updated', 'N/A')}")
        lines.append("=== FIN INFORMACIÓN ===")
        
        return "\n".join(lines)


# Singleton
_service = None

def get_search_service() -> TavilySearchService:
    global _service
    if _service is None:
        _service = TavilySearchService()
    return _service