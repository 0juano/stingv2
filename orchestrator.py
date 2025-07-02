"""Simple orchestrator to process queries through the entire flow"""
import httpx
import asyncio
import json
from typing import Dict, Any
import argparse

class BureaucracyOracle:
    def __init__(self, base_url: str = "http://localhost"):
        self.router_url = f"{base_url}:8001"
        self.auditor_url = f"{base_url}:8005"
        self.total_cost = 0.0
        
    async def process_query(self, question: str) -> Dict[str, Any]:
        """Process a query through the complete flow"""
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
        
        if route_response["decision"]["agent"] == "out_of_scope":
            return {
                "success": False,
                "message": "Query out of scope",
                "flow": flow_data,
                "total_cost": self.total_cost
            }
        
        # Step 2: Call the selected agent
        agent_name = route_response["decision"]["agent"]
        print(f"📞 Calling agent: {agent_name}")
        agent_response = await self._call_agent(agent_name, question)
        flow_data["steps"].append({
            "step": f"agent_{agent_name}",
            "result": agent_response
        })
        
        # Step 3: Audit the response
        print("✅ Auditing response...")
        audit_response = await self._call_auditor(question, agent_response, agent_name)
        flow_data["steps"].append({
            "step": "audit",
            "result": audit_response
        })
        
        # Step 4: Format the response
        formatted = await self._format_response(audit_response)
        
        return {
            "success": True,
            "response": formatted["markdown"],
            "flow": flow_data,
            "total_cost": self.total_cost
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
        # Map agent names to ports
        agent_ports = {
            "bcra": 8002,
            "comex": 8003,
            "senasa": 8004
        }
        
        port = agent_ports.get(agent_name, 8002)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{port}/answer",
                json={"question": question},
                timeout=60.0
            )
            result = response.json()
            self.total_cost += result.get("cost", 0)
            return result
    
    async def _call_auditor(self, question: str, agent_response: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
        """Call the auditor service"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auditor_url}/audit",
                json={
                    "user_question": question,
                    "agent_response": agent_response.get("answer", {}),
                    "agent_name": agent_name
                },
                timeout=60.0
            )
            result = response.json()
            self.total_cost += result.get("cost", 0)
            return result
    
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
    parser = argparse.ArgumentParser(description="Bureaucracy Oracle CLI")
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
            print(f"\n💰 Total cost: ${result['total_cost']:.4f}")
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