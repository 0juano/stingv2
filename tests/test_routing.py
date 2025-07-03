#!/usr/bin/env python3
"""Test routing accuracy of the orchestrator"""
import asyncio
import json
import httpx
from typing import List, Dict
from datetime import datetime

async def test_routing():
    """Test how well the router identifies the correct agent for each question"""
    
    # Load test questions
    with open('test_questions.json', 'r') as f:
        test_cases = json.load(f)
    
    results = []
    correct_routing = 0
    total_queries = len(test_cases)
    
    print("🧪 Testing Bureaucracy Oracle Routing")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        code = test_case['code']
        question = test_case['question']
        expected_agents = [agent.lower() for agent in test_case['agents']]
        
        print(f"\n[{i}/{total_queries}] Question {code}")
        print(f"Expected agents: {', '.join(expected_agents)}")
        
        try:
            # Call router only
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8001/route",
                    json={"question": question},
                    timeout=30.0
                )
                route_result = response.json()
                
            # Try to get agent from different possible fields
            selected_agent = route_result['decision'].get('primary_agent') or route_result['decision'].get('agent')
            confidence = route_result['decision'].get('confidence', 0)
            
            # Check if routing is correct
            is_correct = selected_agent in expected_agents
            if is_correct:
                correct_routing += 1
                status = "✅ CORRECT"
            else:
                status = "❌ WRONG"
            
            print(f"Selected: {selected_agent} (confidence: {confidence:.0%}) {status}")
            
            # Store result
            results.append({
                "code": code,
                "question": question[:80] + "..." if len(question) > 80 else question,
                "expected_agents": expected_agents,
                "selected_agent": selected_agent,
                "confidence": confidence,
                "is_correct": is_correct,
                "status": status
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                "code": code,
                "question": question[:80] + "...",
                "expected_agents": expected_agents,
                "selected_agent": "ERROR",
                "confidence": 0,
                "is_correct": False,
                "status": f"ERROR: {str(e)}"
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 ROUTING TEST SUMMARY")
    print("=" * 60)
    print(f"Total questions: {total_queries}")
    print(f"Correct routing: {correct_routing}/{total_queries} ({correct_routing/total_queries*100:.1f}%)")
    
    # Analyze per agent
    agent_stats = {"bcra": {"total": 0, "selected": 0}, 
                   "comex": {"total": 0, "selected": 0}, 
                   "senasa": {"total": 0, "selected": 0}}
    
    for result in results:
        for agent in result["expected_agents"]:
            if agent in agent_stats:
                agent_stats[agent]["total"] += 1
        
        selected = result["selected_agent"]
        if selected in agent_stats:
            agent_stats[selected]["selected"] += 1
    
    print("\n📈 Agent Distribution:")
    for agent, stats in agent_stats.items():
        print(f"  {agent.upper()}: Expected in {stats['total']} questions, Selected {stats['selected']} times")
    
    # Show incorrect routings
    incorrect = [r for r in results if not r["is_correct"] and r["selected_agent"] != "ERROR"]
    if incorrect:
        print(f"\n❌ Incorrect Routings ({len(incorrect)}):")
        for r in incorrect:
            print(f"  Q{r['code']}: Expected {r['expected_agents']} → Got {r['selected_agent']}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"routing_test_results_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump({
            "summary": {
                "total": total_queries,
                "correct": correct_routing,
                "accuracy": correct_routing/total_queries,
                "timestamp": timestamp
            },
            "details": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {filename}")

if __name__ == "__main__":
    asyncio.run(test_routing())