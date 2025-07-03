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
    
    def needs_search(self, question: str, agent_type: str) -> str:
        """Determine search depth needed: 'none', 'quick', or 'full'"""
        if not self.enabled:
            return "none"
        
        question_lower = question.lower()
        
        # High priority categories that always need search
        ALWAYS_SEARCH_CATEGORIES = [
            "import", "export", "arancel", "límite", "requisito",
            "tarifa", "impuesto", "licencia", "certificado"
        ]
        
        # Check for high-value/complex topics
        has_priority_category = any(cat in question_lower for cat in ALWAYS_SEARCH_CATEGORIES)
        
        # Check temporal triggers
        has_temporal = any(t in question_lower for t in TEMPORAL_TRIGGERS)
        
        # Check agent-specific triggers
        agent_triggers = AGENT_SEARCH_CONFIG.get(agent_type, {}).get("triggers", [])
        has_agent_trigger = any(t in question_lower for t in agent_triggers)
        
        # Determine search depth
        if has_priority_category or has_temporal or has_agent_trigger:
            return "full"  # Full search with 5 results
        else:
            return "quick"  # Quick search with 1 result
    
    async def quick_search(self, query: str, agent_type: str) -> Dict[str, Any]:
        """Perform a quick search with minimal results"""
        return await self.search(query, agent_type, max_results=1, search_depth="basic")
    
    async def search(self, query: str, agent_type: str, max_results: int = 5, search_depth: str = "advanced") -> Dict[str, Any]:
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
            results = await self._execute_search(enhanced_query, config, max_results, search_depth)
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
    
    async def _execute_search(self, query: str, config: Dict, max_results: int, search_depth: str = "advanced") -> Dict:
        """Execute Tavily API search"""
        params = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,  # "basic" for quick, "advanced" for full
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
        from urllib.parse import urlparse
        
        results = raw_results.get("results", [])[:5]
        answer = raw_results.get("answer", "")
        
        processed = {
            "summary": answer,
            "sources": [],
            "key_facts": [],
            "last_updated": datetime.now().isoformat(),
            "sources_consulted": []  # Track actual sources for display
        }
        
        for result in results:
            source = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:500],
                "score": result.get("score", 0)
            }
            processed["sources"].append(source)
            
            # Extract domain and key info for display
            if result.get("url"):
                domain = urlparse(result["url"]).netloc
                # Extract regulation numbers from title or content
                text = f"{result.get('title', '')} {result.get('content', '')}"
                regulations = re.findall(r'(?:Resolución|Comunicación|Decreto|NCM)\s*(?:N°|Nº|A)?\s*[\d\./-]+', text)
                
                if regulations:
                    for reg in regulations[:2]:  # Max 2 per source
                        processed["sources_consulted"].append(f"{domain} ({reg})")
                else:
                    processed["sources_consulted"].append(domain)
            
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
        
        import re
        
        lines = ["📊 INFORMACIÓN ACTUALIZADA DE BÚSQUEDA WEB:"]
        lines.append("⚠️ IMPORTANTE: Usa estos valores EXACTAMENTE como aparecen:\n")
        
        # Extract and highlight numeric values from all sources
        all_percentages = set()
        all_amounts = set()
        
        for source in search_results.get("sources", [])[:3]:
            content = source.get("content", "")
            # Extract percentages (e.g., 16%, 10.5%)
            percentages = re.findall(r'(\d+(?:\.\d+)?%)', content)
            all_percentages.update(percentages)
            
            # Extract USD amounts
            usd_amounts = re.findall(r'USD?\s*(\d+(?:\.\d+)?)', content)
            all_amounts.update(usd_amounts)
        
        # Show extracted values prominently
        if all_percentages:
            lines.append("✓ PORCENTAJES ENCONTRADOS: " + ", ".join(sorted(all_percentages)))
        if all_amounts:
            lines.append("✓ MONTOS USD ENCONTRADOS: " + ", ".join(sorted(all_amounts)[:5]))
        
        if all_percentages or all_amounts:
            lines.append("")
        
        # Add summary if available
        if search_results.get("summary"):
            lines.append(f"RESUMEN: {search_results['summary']}\n")
        
        # Add key facts
        if search_results.get("key_facts"):
            lines.append("DATOS CLAVE:")
            lines.extend(f"• {fact}" for fact in search_results["key_facts"])
            lines.append("")
        
        # Add sources with highlighted values
        if search_results.get("sources"):
            lines.append("FUENTES VERIFICADAS:")
            for i, source in enumerate(search_results["sources"][:3], 1):
                lines.append(f"\n{i}. {source['title']}")
                lines.append(f"   URL: {source['url']}")
                
                # Highlight numeric values in content preview
                content_preview = source['content'][:200]
                # Bold percentages in content
                content_preview = re.sub(r'(\d+(?:\.\d+)?%)', r'**\1**', content_preview)
                lines.append(f"   Contenido: {content_preview}...")
        
        lines.append(f"\nActualizado: {search_results.get('last_updated', 'N/A')}")
        lines.append("=== FIN INFORMACIÓN DE BÚSQUEDA ===")
        
        return "\n".join(lines)


# Singleton
_service = None

def get_search_service() -> TavilySearchService:
    global _service
    if _service is None:
        _service = TavilySearchService()
    return _service