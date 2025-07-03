#!/usr/bin/env python3
"""
A/B Test for Search Integration
Tests agent responses with and without search enabled
"""
import asyncio
import json
import os
import time
from datetime import datetime
import httpx
from typing import Dict, List, Any
import subprocess
import sys

# Test questions that likely need current information
SEARCH_SENSITIVE_QUESTIONS = [
    # COMEX - Tariff/NCM questions
    {
        "question": "¿Qué arancel tiene la importación de notebooks y laptops?",
        "agents": ["comex"],
        "search_keywords": ["arancel", "notebooks", "NCM 8471.30"]
    },
    {
        "question": "¿Cuál es el arancel actual para importar teléfonos celulares?",
        "agents": ["comex"],
        "search_keywords": ["arancel", "celulares", "actual"]
    },
    {
        "question": "¿Qué impuestos paga hoy la importación de ropa desde China?",
        "agents": ["comex"],
        "search_keywords": ["impuestos", "ropa", "China", "hoy"]
    },
    
    # BCRA - Limits and exchange rates
    {
        "question": "¿Cuál es el límite actual para pagar servicios digitales como Netflix?",
        "agents": ["bcra"],
        "search_keywords": ["límite", "actual", "servicios digitales"]
    },
    {
        "question": "¿Cuál es la cotización del dólar MEP hoy?",
        "agents": ["bcra"],
        "search_keywords": ["cotización", "dólar MEP", "hoy"]
    },
    {
        "question": "¿Cuáles son los límites vigentes para compra de dólares ahorro?",
        "agents": ["bcra"],
        "search_keywords": ["límites", "vigentes", "dólares ahorro"]
    },
    
    # SENASA - Current protocols
    {
        "question": "¿Cuáles son los requisitos actuales para exportar limones a Europa?",
        "agents": ["senasa"],
        "search_keywords": ["requisitos", "actuales", "limones", "Europa"]
    },
    {
        "question": "¿Qué protocolo sanitario vigente aplica para exportar carne a China?",
        "agents": ["senasa"],
        "search_keywords": ["protocolo", "vigente", "carne", "China"]
    },
    
    # Multi-agent with current info
    {
        "question": "¿Cómo importar notebooks en 2024 y cuánto puedo pagar al proveedor?",
        "agents": ["comex", "bcra"],
        "search_keywords": ["importar", "notebooks", "2024", "pagar"]
    },
    {
        "question": "Para exportar vino a Brasil, ¿qué arancel paga y cómo liquido las divisas hoy?",
        "agents": ["comex", "bcra"],
        "search_keywords": ["exportar", "vino", "Brasil", "hoy"]
    }
]

class SearchABTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.results = {
            "test_date": datetime.now().isoformat(),
            "questions_tested": len(SEARCH_SENSITIVE_QUESTIONS),
            "with_search": [],
            "without_search": [],
            "comparison": []
        }
    
    async def test_question(self, question: str, enable_search: bool) -> Dict[str, Any]:
        """Test a single question with or without search"""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/process",
                    json={"question": question},
                    headers={"X-Enable-Search": str(enable_search).lower()}
                )
                response.raise_for_status()
                result = response.json()
                
                duration = time.time() - start_time
                
                return {
                    "question": question,
                    "response": result.get("response", ""),
                    "agents_used": result.get("agents_used", []),
                    "duration": round(duration, 2),
                    "cost": result.get("total_cost", 0),
                    "confidence": result.get("confidence", 0),
                    "search_enabled": enable_search,
                    "error": None
                }
                
        except Exception as e:
            return {
                "question": question,
                "response": None,
                "duration": time.time() - start_time,
                "search_enabled": enable_search,
                "error": str(e)
            }
    
    def toggle_search(self, enable: bool):
        """Toggle search feature in .env file"""
        env_path = "/Users/juanotero/Documents/GitHub/stingv2/.env"
        
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith("ENABLE_SEARCH="):
                    f.write(f"ENABLE_SEARCH={'true' if enable else 'false'}\n")
                else:
                    f.write(line)
        
        # Restart services to apply changes
        print(f"{'Enabling' if enable else 'Disabling'} search...")
        subprocess.run(["docker-compose", "restart"], capture_output=True)
        time.sleep(5)  # Wait for services to restart
    
    async def run_tests(self):
        """Run A/B tests"""
        print("Starting A/B Test for Search Integration")
        print("=" * 50)
        
        # Test WITHOUT search first
        print("\n📊 Testing WITHOUT search enabled...")
        self.toggle_search(False)
        
        for i, test_case in enumerate(SEARCH_SENSITIVE_QUESTIONS, 1):
            print(f"\n[{i}/{len(SEARCH_SENSITIVE_QUESTIONS)}] Testing: {test_case['question'][:60]}...")
            result = await self.test_question(test_case["question"], False)
            self.results["without_search"].append(result)
            
            if result["error"]:
                print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   ✅ Response in {result['duration']}s")
        
        # Test WITH search
        print("\n\n📊 Testing WITH search enabled...")
        self.toggle_search(True)
        
        for i, test_case in enumerate(SEARCH_SENSITIVE_QUESTIONS, 1):
            print(f"\n[{i}/{len(SEARCH_SENSITIVE_QUESTIONS)}] Testing: {test_case['question'][:60]}...")
            result = await self.test_question(test_case["question"], True)
            self.results["with_search"].append(result)
            
            if result["error"]:
                print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   ✅ Response in {result['duration']}s")
        
        # Compare results
        self.compare_results()
        
        # Save results
        self.save_results()
        
        # Reset to original state
        self.toggle_search(False)
    
    def compare_results(self):
        """Compare results between search and no-search"""
        print("\n\n📈 COMPARISON RESULTS")
        print("=" * 50)
        
        for i, (with_search, without_search) in enumerate(
            zip(self.results["with_search"], self.results["without_search"])
        ):
            comparison = {
                "question": with_search["question"],
                "time_difference": with_search["duration"] - without_search["duration"],
                "time_with_search": with_search["duration"],
                "time_without_search": without_search["duration"],
                "search_overhead_seconds": with_search["duration"] - without_search["duration"],
                "search_overhead_percent": ((with_search["duration"] - without_search["duration"]) / without_search["duration"] * 100) if without_search["duration"] > 0 else 0,
                "search_added_value": False,
                "key_differences": []
            }
            
            # Check for key improvements
            if with_search["response"] and without_search["response"]:
                with_response = with_search["response"].lower()
                without_response = without_search["response"].lower()
                
                # Check for specific improvements
                if "2024" in with_response and "2024" not in without_response:
                    comparison["key_differences"].append("Contains 2024 information")
                    comparison["search_added_value"] = True
                
                if "2023" in without_response and "2024" in with_response:
                    comparison["key_differences"].append("Updated from 2023 to 2024 data")
                    comparison["search_added_value"] = True
                
                # Check for specific values (like tariffs)
                import re
                with_percentages = set(re.findall(r'\d+(?:\.\d+)?%', with_response))
                without_percentages = set(re.findall(r'\d+(?:\.\d+)?%', without_response))
                
                if with_percentages != without_percentages:
                    comparison["key_differences"].append(
                        f"Different values: {without_percentages} → {with_percentages}"
                    )
                    comparison["search_added_value"] = True
            
            self.results["comparison"].append(comparison)
            
            # Print summary
            print(f"\nQuestion {i+1}: {comparison['question'][:60]}...")
            print(f"  ⏱️  Time WITHOUT search: {comparison['time_without_search']:.2f}s")
            print(f"  ⏱️  Time WITH search: {comparison['time_with_search']:.2f}s")
            print(f"  📊 Search overhead: +{comparison['search_overhead_seconds']:.2f}s ({comparison['search_overhead_percent']:.1f}% increase)")
            print(f"  ✨ Search added value: {'YES' if comparison['search_added_value'] else 'NO'}")
            if comparison["key_differences"]:
                print(f"  🔍 Key differences: {', '.join(comparison['key_differences'])}")
    
    def save_results(self):
        """Save test results to file"""
        filename = f"search_ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Calculate summary statistics
        with_search_times = [r["duration"] for r in self.results["with_search"] if not r["error"]]
        without_search_times = [r["duration"] for r in self.results["without_search"] if not r["error"]]
        
        # Calculate search overhead statistics
        search_overheads = [c["search_overhead_seconds"] for c in self.results["comparison"]]
        search_overhead_percents = [c["search_overhead_percent"] for c in self.results["comparison"]]
        
        self.results["summary"] = {
            "avg_time_with_search": sum(with_search_times) / len(with_search_times) if with_search_times else 0,
            "avg_time_without_search": sum(without_search_times) / len(without_search_times) if without_search_times else 0,
            "avg_search_overhead_seconds": sum(search_overheads) / len(search_overheads) if search_overheads else 0,
            "avg_search_overhead_percent": sum(search_overhead_percents) / len(search_overhead_percents) if search_overhead_percents else 0,
            "min_search_overhead": min(search_overheads) if search_overheads else 0,
            "max_search_overhead": max(search_overheads) if search_overheads else 0,
            "questions_improved": sum(1 for c in self.results["comparison"] if c["search_added_value"]),
            "total_questions": len(self.results["comparison"])
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n\n✅ Results saved to: {filename}")
        print("\n📊 SUMMARY:")
        print(f"  Average time WITHOUT search: {self.results['summary']['avg_time_without_search']:.2f}s")
        print(f"  Average time WITH search: {self.results['summary']['avg_time_with_search']:.2f}s")
        print(f"  Average search overhead: +{self.results['summary']['avg_search_overhead_seconds']:.2f}s ({self.results['summary']['avg_search_overhead_percent']:.1f}% increase)")
        print(f"  Search overhead range: {self.results['summary']['min_search_overhead']:.2f}s to {self.results['summary']['max_search_overhead']:.2f}s")
        print(f"  Questions improved by search: {self.results['summary']['questions_improved']}/{self.results['summary']['total_questions']} ({self.results['summary']['questions_improved']/self.results['summary']['total_questions']*100:.0f}%)")


async def main():
    """Run the A/B test"""
    # Check if services are running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/health")
            response.raise_for_status()
    except:
        print("❌ Services not running. Please run 'make dev' first.")
        sys.exit(1)
    
    tester = SearchABTester()
    await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())