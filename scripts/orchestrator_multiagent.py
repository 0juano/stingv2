"""Multi-agent orchestrator with parallel processing"""
import httpx
import asyncio
import json
from typing import Dict, Any, List
import argparse

class BureaucracyOracle:
    def __init__(self, base_url: str = "http://localhost"):
        self.router_url = f"{base_url}:8001"
        self.auditor_url = f"{base_url}:8005"
        self.total_cost = 0.0
        
    async def process_query(self, question: str) -> Dict[str, Any]:
        """Process a query through the complete flow with multi-agent support"""
        flow_data = {
            "question": question,
            "steps": []
        }
        
        # Step 1: Route the query
        print(f"🔄 Routing query: {question}")
        route_response = await self._call_router(question)
        flow_data["steps"].append({
            "step": "routing",
            "result": route_response
        })
        
        # Extract agents from new format
        decision = route_response["decision"]
        agents = decision.get("agents", [])
        primary_agent = decision.get("primary_agent", "")
        
        # Backward compatibility - if using old format
        if "agent" in decision and not agents:
            agents = [decision["agent"]] if decision["agent"] != "out_of_scope" else []
            primary_agent = decision["agent"]
        
        if not agents or primary_agent == "out_of_scope":
            return {
                "success": False,
                "message": "Query out of scope",
                "flow": flow_data,
                "total_cost": self.total_cost
            }
        
        # Step 2: Call multiple agents in PARALLEL
        print(f"📞 Calling {len(agents)} agent(s) in parallel: {', '.join(agents)}")
        
        # Create tasks for parallel execution
        agent_tasks = [
            self._call_agent(agent_name, question) 
            for agent_name in agents
        ]
        
        # Execute all agent calls in parallel
        agent_responses_list = await asyncio.gather(*agent_tasks)
        
        # Build agent responses dictionary
        agent_responses = {}
        for agent_name, response in zip(agents, agent_responses_list):
            agent_responses[agent_name] = response
            flow_data["steps"].append({
                "step": f"agent_{agent_name}",
                "result": response
            })
        
        # Step 3: Audit the combined responses
        print("✅ Auditing combined responses...")
        audit_response = await self._call_auditor_multi(
            question, agent_responses, primary_agent
        )
        flow_data["steps"].append({
            "step": "audit",
            "result": audit_response
        })
        
        # Step 4: Format the response
        formatted = await self._format_response(audit_response)
        
        return {
            "success": True,
            "response": formatted.get("markdown", "Error formatting response"),
            "flow": flow_data,
            "total_cost": self.total_cost,
            "agents_consulted": list(agents)
        }
    
    async def _call_router(self, question: str) -> Dict[str, Any]:
        """Call the router service"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.router_url}/route",
                json={"question": question},
                timeout=60.0
            )
            result = response.json()
            self.total_cost += result.get("cost", 0)
            return result
    
    async def _call_agent(self, agent_name: str, question: str) -> Dict[str, Any]:
        """Call a specific agent"""
        agent_ports = {
            "bcra": 8002,
            "comex": 8003,
            "senasa": 8004
        }
        
        port = agent_ports.get(agent_name, 8002)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:{port}/answer",
                    json={"question": question},
                    timeout=60.0
                )
                result = response.json()
                self.total_cost += result.get("cost", 0)
                return result
        except Exception as e:
            print(f"⚠️ Error calling {agent_name}: {str(e)}")
            return {
                "answer": {"error": f"Failed to contact {agent_name}"},
                "agent": agent_name,
                "cost": 0,
                "error": str(e)
            }
    
    async def _call_auditor_multi(
        self, 
        question: str, 
        agent_responses: Dict[str, Dict[str, Any]], 
        primary_agent: str
    ) -> Dict[str, Any]:
        """Call the auditor service with multiple agent responses"""
        async with httpx.AsyncClient() as client:
            # For backward compatibility, check if auditor supports multi-agent
            # First try the multi-agent endpoint
            try:
                response = await client.post(
                    f"{self.auditor_url}/audit-multi",
                    json={
                        "user_question": question,
                        "agent_responses": agent_responses,
                        "primary_agent": primary_agent
                    },
                    timeout=60.0
                )
                result = response.json()
                self.total_cost += result.get("cost", 0)
                return result
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # Fallback to single agent for primary agent only
                    print("⚠️ Multi-agent audit not available, using primary agent only")
                    primary_response = agent_responses.get(primary_agent, {})
                    response = await client.post(
                        f"{self.auditor_url}/audit",
                        json={
                            "user_question": question,
                            "agent_response": primary_response.get("answer", {}),
                            "agent_name": primary_agent
                        },
                        timeout=60.0
                    )
                    result = response.json()
                    self.total_cost += result.get("cost", 0)
                    return result
                else:
                    raise
    
    async def _format_response(self, audit_response: Dict[str, Any]) -> Dict[str, Any]:
        """Format the final response"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auditor_url}/format",
                json=audit_response,
                timeout=60.0
            )
            return response.json()

async def main():
    parser = argparse.ArgumentParser(description="Bureaucracy Oracle CLI - Multi-Agent")
    parser.add_argument("question", help="Your question about Argentine regulations")
    parser.add_argument("--debug", action="store_true", help="Show debug information")
    args = parser.parse_args()
    
    oracle = BureaucracyOracle()
    
    try:
        result = await oracle.process_query(args.question)
        
        if result["success"]:
            print("\n" + "="*50)
            print(result["response"])
            print("="*50)
            
            # Show which agents were consulted
            if "agents_consulted" in result:
                agents = result["agents_consulted"]
                print(f"\n🤝 Agents consulted: {', '.join(agents)}")
            
            print(f"💰 Total cost: ${result['total_cost']:.4f}")
        else:
            print(f"\n❌ {result['message']}")
        
        if args.debug:
            print("\n🔍 Debug Information:")
            print(json.dumps(result["flow"], indent=2, ensure_ascii=False))
    
    except httpx.ReadTimeout:
        print(f"\n❌ Error: Request timed out. The service might be processing a complex query.")
        print("\nTry again with a simpler question or check the logs:")
        print("  make logs")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("\nMake sure all services are running:")
        print("  docker-compose up")

if __name__ == "__main__":
    asyncio.run(main())