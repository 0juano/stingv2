"""Base template for all agent services"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agent Service")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    context: Dict[str, Any] = Field(default_factory=dict)

class QueryResponse(BaseModel):
    answer: Dict[str, Any]
    agent: str
    model: str
    cost: float = 0.0
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    agent: str
    model: str

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        agent=os.getenv("AGENT_NAME", "unknown"),
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    )

@app.post("/answer", response_model=QueryResponse)
async def answer(query: QueryRequest):
    """Process a query and return structured answer"""
    agent_name = os.getenv("AGENT_NAME", "unknown")
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not configured")
    
    # Load prompt
    prompt_path = Path("prompt.md")
    if not prompt_path.exists():
        raise HTTPException(status_code=500, detail="prompt.md not found")
    
    prompt = prompt_path.read_text()
    
    # Prepare messages
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": query.question}
    ]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://github.com/bureaucracy-oracle",
                    "X-Title": "Bureaucracy Oracle"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.1,  # Low temperature for consistency
                    "response_format": {"type": "json_object"}  # Force JSON response
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract cost from headers
            cost = float(response.headers.get("x-openrouter-cost", 0))
            
            # Parse the assistant's response
            try:
                answer_content = json.loads(result["choices"][0]["message"]["content"])
            except json.JSONDecodeError:
                # Fallback if response isn't valid JSON
                answer_content = {
                    "response": result["choices"][0]["message"]["content"],
                    "error": "Response was not valid JSON"
                }
            
            return QueryResponse(
                answer=answer_content,
                agent=agent_name,
                model=model,
                cost=cost
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenRouter API error: {e.response.text}")
        return QueryResponse(
            answer={"error": f"API error: {e.response.status_code}"},
            agent=agent_name,
            model=model,
            error=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return QueryResponse(
            answer={"error": "Internal error"},
            agent=agent_name,
            model=model,
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)