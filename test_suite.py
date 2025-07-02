#!/usr/bin/env python3
"""Full test suite for the bureaucracy oracle - tests complete flow"""
import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from orchestrator import BureaucracyOracle

class TestSuite:
    def __init__(self):
        self.oracle = BureaucracyOracle()
        self.results = []
        self.start_time = None
        self.total_cost = 0.0
        
    async def run_test(self, test_case: Dict[str, Any], index: int, total: int) -> Dict[str, Any]:
        """Run a single test case through the complete flow"""
        code = test_case['code']
        question = test_case['question']
        expected_agents = [agent.lower() for agent in test_case['agents']]
        
        print(f"\n[{index}/{total}] Testing Q{code}")
        print(f"Question: {question[:80]}{'...' if len(question) > 80 else ''}")
        print(f"Expected agents: {', '.join(expected_agents)}")
        
        start_time = time.time()
        result = {
            "code": code,
            "question": question,
            "expected_agents": expected_agents,
            "success": False,
            "error": None,
            "timing": {}
        }
        
        try:
            # Run through orchestrator
            response = await self.oracle.process_query(question)
            elapsed = time.time() - start_time
            
            result["success"] = response.get("success", False)
            result["total_time"] = elapsed
            result["cost"] = response.get("total_cost", 0)
            
            if response.get("flow"):
                # Extract routing info
                routing_step = next((s for s in response["flow"]["steps"] if s["step"] == "routing"), None)
                if routing_step:
                    selected_agent = routing_step["result"]["decision"]["agent"]
                    confidence = routing_step["result"]["decision"]["confidence"]
                    result["selected_agent"] = selected_agent
                    result["confidence"] = confidence
                    result["routing_correct"] = selected_agent in expected_agents
                    print(f"Routed to: {selected_agent} (confidence: {confidence:.0%})")
                
                # Extract agent response
                agent_step = next((s for s in response["flow"]["steps"] if s["step"].startswith("agent_")), None)
                if agent_step:
                    agent_answer = agent_step["result"].get("answer", {})
                    result["agent_response"] = agent_answer
                    result["has_insufficient_context"] = "INSUFFICIENT_CONTEXT" in str(agent_answer)
                
                # Extract audit result
                audit_step = next((s for s in response["flow"]["steps"] if s["step"] == "audit"), None)
                if audit_step:
                    result["audit_status"] = audit_step["result"].get("status", "Unknown")
            
            if result["success"]:
                print(f"✅ Success in {elapsed:.1f}s (${result['cost']:.4f})")
            else:
                print(f"❌ Failed: {response.get('message', 'Unknown error')}")
                
        except asyncio.TimeoutError:
            result["error"] = "Timeout"
            result["total_time"] = time.time() - start_time
            print(f"⏱️ Timeout after {result['total_time']:.1f}s")
        except Exception as e:
            result["error"] = str(e)
            result["total_time"] = time.time() - start_time
            print(f"❌ Error: {str(e)}")
        
        self.total_cost += result.get("cost", 0)
        return result
    
    async def run_all_tests(self):
        """Run all test cases"""
        print("🧪 BUREAUCRACY ORACLE FULL TEST SUITE")
        print("=" * 70)
        
        # Load test questions
        with open('test_questions.json', 'r') as f:
            test_cases = json.load(f)
        
        self.start_time = time.time()
        
        # Run tests sequentially
        for i, test_case in enumerate(test_cases, 1):
            result = await self.run_test(test_case, i, len(test_cases))
            self.results.append(result)
            
            # Small delay to avoid rate limiting
            if i < len(test_cases):
                await asyncio.sleep(1)
        
        total_time = time.time() - self.start_time
        
        # Generate report
        self.generate_report(total_time)
    
    def generate_report(self, total_time: float):
        """Generate comprehensive test report"""
        print("\n" + "=" * 70)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 70)
        
        # Calculate metrics
        total_tests = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        routing_correct = sum(1 for r in self.results if r.get("routing_correct", False))
        timeouts = sum(1 for r in self.results if r.get("error") == "Timeout")
        insufficient_context = sum(1 for r in self.results if r.get("has_insufficient_context", False))
        
        print(f"\n📈 Overall Metrics:")
        print(f"  Total Questions: {total_tests}")
        print(f"  Successful: {successful}/{total_tests} ({successful/total_tests*100:.1f}%)")
        print(f"  Routing Accuracy: {routing_correct}/{total_tests} ({routing_correct/total_tests*100:.1f}%)")
        print(f"  Timeouts: {timeouts}")
        print(f"  Insufficient Context: {insufficient_context}")
        print(f"  Total Cost: ${self.total_cost:.4f}")
        print(f"  Total Time: {total_time:.1f}s")
        print(f"  Avg Time/Query: {total_time/total_tests:.1f}s")
        
        # Per-agent analysis
        agent_stats = {}
        for result in self.results:
            agent = result.get("selected_agent", "unknown")
            if agent not in agent_stats:
                agent_stats[agent] = {
                    "count": 0,
                    "successful": 0,
                    "total_time": 0,
                    "total_cost": 0,
                    "insufficient_context": 0
                }
            
            agent_stats[agent]["count"] += 1
            if result["success"]:
                agent_stats[agent]["successful"] += 1
            agent_stats[agent]["total_time"] += result.get("total_time", 0)
            agent_stats[agent]["total_cost"] += result.get("cost", 0)
            if result.get("has_insufficient_context"):
                agent_stats[agent]["insufficient_context"] += 1
        
        print(f"\n📊 Per-Agent Performance:")
        for agent, stats in sorted(agent_stats.items()):
            if stats["count"] > 0:
                avg_time = stats["total_time"] / stats["count"]
                success_rate = stats["successful"] / stats["count"] * 100
                print(f"  {agent.upper()}:")
                print(f"    - Queries: {stats['count']}")
                print(f"    - Success Rate: {success_rate:.1f}%")
                print(f"    - Avg Time: {avg_time:.1f}s")
                print(f"    - Total Cost: ${stats['total_cost']:.4f}")
                print(f"    - Insufficient Context: {stats['insufficient_context']}")
        
        # Routing accuracy by expected agent
        print(f"\n🎯 Routing Accuracy by Expected Agent:")
        expected_stats = {"bcra": {"total": 0, "correct": 0}, 
                         "comex": {"total": 0, "correct": 0}, 
                         "senasa": {"total": 0, "correct": 0}}
        
        for result in self.results:
            for agent in result["expected_agents"]:
                if agent in expected_stats:
                    expected_stats[agent]["total"] += 1
                    if result.get("routing_correct", False):
                        expected_stats[agent]["correct"] += 1
        
        for agent, stats in expected_stats.items():
            if stats["total"] > 0:
                accuracy = stats["correct"] / stats["total"] * 100
                print(f"  {agent.upper()}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
        
        # Failed queries
        failed = [r for r in self.results if not r["success"] or r.get("error")]
        if failed:
            print(f"\n❌ Failed Queries ({len(failed)}):")
            for r in failed[:5]:  # Show first 5
                print(f"  Q{r['code']}: {r.get('error', 'Unknown error')}")
            if len(failed) > 5:
                print(f"  ... and {len(failed)-5} more")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_suite_results_{timestamp}.json"
        
        report_data = {
            "summary": {
                "timestamp": timestamp,
                "total_tests": total_tests,
                "successful": successful,
                "routing_accuracy": routing_correct / total_tests,
                "total_cost": self.total_cost,
                "total_time": total_time,
                "agent_stats": agent_stats,
                "expected_stats": expected_stats
            },
            "details": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed results saved to: {filename}")

async def main():
    """Run the full test suite"""
    print("Starting Bureaucracy Oracle Test Suite...")
    print("This will test all 30 questions through the complete flow.")
    print("Estimated time: 5-10 minutes\n")
    
    suite = TestSuite()
    await suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())