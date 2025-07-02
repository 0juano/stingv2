"""Router service - routes queries to appropriate agents"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import json
import yaml
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Router Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RouteRequest(BaseModel):
    question: str

class RouteDecision(BaseModel):
    agent: str
    reason: str
    confidence: float = 0.0

class RouteResponse(BaseModel):
    decision: RouteDecision
    agents_available: List[str]
    cost: float = 0.0

# Load agents configuration
def load_agents_config():
    """Load agents configuration from agents.yml"""
    try:
        with open("/app/agents.yml", "r") as f:
            config = yaml.safe_load(f)
            return config.get("agents", [])
    except Exception as e:
        logger.error(f"Failed to load agents.yml: {e}")
        return []

@app.get("/health")
async def health():
    """Health check endpoint"""
    agents = load_agents_config()
    return {
        "status": "healthy",
        "service": "router",
        "agents_configured": len(agents)
    }

@app.post("/route", response_model=RouteResponse)
async def route(request: RouteRequest):
    """Route query to appropriate agent"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not configured")
    
    # Load available agents
    agents = load_agents_config()
    agent_names = [agent["slug"] for agent in agents]
    
    # Load routing prompt
    try:
        with open("/app/prompt.md", "r") as f:
            base_prompt = f.read()
    except:
        # Fallback prompt if file not found
        base_prompt = """You are a routing agent for Argentine regulations.
Available agents: bcra, comex, senasa.
Route to the most appropriate agent."""
    
    # Agent bias adjustment (can be configured via env vars)
    agent_biases = {
        "bcra": float(os.getenv("ROUTER_BIAS_BCRA", "1.0")),
        "comex": float(os.getenv("ROUTER_BIAS_COMEX", "1.0")),
        "senasa": float(os.getenv("ROUTER_BIAS_SENASA", "1.0"))
    }
    
    bias_note = ""
    if any(bias != 1.0 for bias in agent_biases.values()):
        bias_note = f"\n\nBias adjustments: {agent_biases}"
    
    routing_prompt = f"{base_prompt}{bias_note}\n\nQuestion: {request.question}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://github.com/bureaucracy-oracle",
                    "X-Title": "Bureaucracy Oracle Router"
                },
                json={
                    "model": os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
                    "messages": [
                        {"role": "system", "content": routing_prompt}
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract cost
            cost = float(response.headers.get("x-openrouter-cost", 0))
            
            # Parse routing decision
            decision_data = json.loads(result["choices"][0]["message"]["content"])
            # Ensure agent name is lowercase
            if "agent" in decision_data:
                decision_data["agent"] = decision_data["agent"].lower()
            decision = RouteDecision(**decision_data)
            
            return RouteResponse(
                decision=decision,
                agents_available=agent_names,
                cost=cost
            )
            
    except Exception as e:
        logger.error(f"Routing error: {str(e)}")
        # Default to out_of_scope on error
        return RouteResponse(
            decision=RouteDecision(
                agent="out_of_scope",
                reason="Error al procesar la consulta",
                confidence=0.0
            ),
            agents_available=agent_names,
            cost=0.0
        )

@app.get("/agents")
async def get_agents():
    """Get list of available agents"""
    agents = load_agents_config()
    return {"agents": agents}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)