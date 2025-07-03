from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import os

app = FastAPI()

ROUTER_URL = "http://localhost:8001"

@app.get("/")
async def root():
    return {"message": "Bureaucracy Oracle API", "router": f"{ROUTER_URL}/docs"}

@app.get("/health")
async def health():
    # Check all services
    services = {
        "router": 8001,
        "bcra": 8002,
        "comex": 8003,
        "senasa": 8004,
        "auditor": 8005
    }
    
    status = {}
    for service, port in services.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:{port}/health")
                status[service] = response.status_code == 200
        except:
            status[service] = False
    
    all_healthy = all(status.values())
    return JSONResponse(
        content={"services": status, "healthy": all_healthy},
        status_code=200 if all_healthy else 503
    )

@app.post("/query")
async def query(request: Request):
    # Proxy to router
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{ROUTER_URL}/query", json=body)
        return response.json()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting proxy server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
