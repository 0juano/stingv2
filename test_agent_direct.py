#!/usr/bin/env python3
"""Test agent directly with OpenRouter API"""
import httpx
import os
import json

async def test_bcra_direct():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set")
        return
        
    prompt = """Eres un experto en regulaciones del BCRA Argentina.
    
Pregunta: ¿Cuál es el límite mensual para comprar dólares para ahorro en Argentina?

Responde en JSON con este formato:
{
  "Respuesta": "respuesta clara",
  "MontoLimite": "monto en USD"
}"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/test",
                "X-Title": "Test"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": prompt}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if "choices" in result:
            content = result["choices"][0]["message"]["content"]
            print(f"Response: {content}")
        else:
            print(f"Error: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_bcra_direct())