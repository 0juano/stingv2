"""Auditor service - validates and summarizes agent responses"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import json
from typing import Dict, Any, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auditor Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuditRequest(BaseModel):
    user_question: str
    agent_response: Dict[str, Any]
    agent_name: str

class FormattedResponse(BaseModel):
    titulo: str
    respuesta_directa: str
    detalles: List[str]
    normativa_aplicable: List[str]
    proxima_accion: str
    advertencias: Optional[str] = None

class AuditResponse(BaseModel):
    status: str  # Aprobado, Observado, Rechazado
    motivo_auditoria: str
    respuesta_final: FormattedResponse
    metadata: Dict[str, Any]
    cost: float = 0.0

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "auditor",
        "model": os.getenv("OPENROUTER_MODEL", "openai/gpt-4o")
    }

@app.post("/audit", response_model=AuditResponse)
async def audit(request: AuditRequest):
    """Audit and format agent response"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not configured")
    
    # Create audit prompt
    audit_prompt = f"""Eres el **Auditor y Resumidor Final** del Oráculo Burocrático Argentino.

Tu misión:
1. AUDITAR: Verificar exactitud y completitud de la respuesta del agente
2. RESUMIR: Crear una respuesta final clara y útil para el usuario

Datos recibidos:
- Pregunta del usuario: {request.user_question}
- Respuesta del agente {request.agent_name}: {json.dumps(request.agent_response, ensure_ascii=False)}

Proceso de Auditoría:
1. Verifica que la respuesta aborde la consulta directamente
2. Valida que las citas normativas tengan formato correcto
3. Asegura que la información sea precisa y completa

Proceso de Resumen:
Crea una respuesta con:
- Título descriptivo con emoji
- Respuesta directa en 1-2 oraciones
- Detalles clave en bullets
- Normativa citada
- Próxima acción clara

Responde con JSON:
{{
  "status": "Aprobado|Observado|Rechazado",
  "motivo_auditoria": "<máx 20 palabras>",
  "respuesta_final": {{
    "titulo": "🎯 <Título de 5-8 palabras>",
    "respuesta_directa": "✅ <Lo esencial en 1-2 oraciones>",
    "detalles": [
      "📌 <detalle clave 1>",
      "📌 <detalle clave 2>",
      "📌 <detalle clave 3>"
    ],
    "normativa_aplicable": [
      "📋 <norma 1 con número y año>",
      "📋 <norma 2 con número y año>"
    ],
    "proxima_accion": "👉 <Qué hacer ahora mismo>",
    "advertencias": "⚠️ <Solo si hay algo crítico>"
  }},
  "metadata": {{
    "agente_consultado": "{request.agent_name}",
    "confianza": 0.95
  }}
}}"""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://github.com/bureaucracy-oracle",
                    "X-Title": "Bureaucracy Oracle Auditor"
                },
                json={
                    "model": os.getenv("OPENROUTER_MODEL", "openai/gpt-4o"),
                    "messages": [
                        {"role": "system", "content": audit_prompt}
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
            
            # Parse audit result
            audit_data = json.loads(result["choices"][0]["message"]["content"])
            
            # Handle cases where the response might not have all fields
            if "respuesta_final" not in audit_data:
                audit_data["respuesta_final"] = {
                    "titulo": "❌ Error en procesamiento",
                    "respuesta_directa": "No se pudo procesar la respuesta correctamente",
                    "detalles": ["Error al auditar la respuesta del agente"],
                    "normativa_aplicable": [],
                    "proxima_accion": "Por favor, intente nuevamente"
                }
            
            # Build response
            formatted = FormattedResponse(**audit_data["respuesta_final"])
            
            return AuditResponse(
                status=audit_data.get("status", "Rechazado"),
                motivo_auditoria=audit_data.get("motivo_auditoria", "Error en auditoría"),
                respuesta_final=formatted,
                metadata=audit_data.get("metadata", {"agente_consultado": request.agent_name}),
                cost=cost
            )
            
    except Exception as e:
        logger.error(f"Audit error: {str(e)}")
        # Return a safe error response
        return AuditResponse(
            status="Rechazado",
            motivo_auditoria="Error en el proceso de auditoría",
            respuesta_final=FormattedResponse(
                titulo="❌ Error de Sistema",
                respuesta_directa="Hubo un error al procesar su consulta",
                detalles=["El sistema no pudo completar la auditoría"],
                normativa_aplicable=[],
                proxima_accion="Por favor, intente nuevamente en unos momentos"
            ),
            metadata={"agente_consultado": request.agent_name, "error": str(e)},
            cost=0.0
        )

@app.post("/format")
async def format_response(audit_response: AuditResponse):
    """Format audit response as markdown"""
    r = audit_response.respuesta_final
    
    markdown = f"""{r.titulo}

{r.respuesta_directa}

**Información Clave:**
"""
    
    for detalle in r.detalles:
        markdown += f"{detalle}\n"
    
    if r.normativa_aplicable:
        markdown += "\n**Normativa Aplicable:**\n"
        for norma in r.normativa_aplicable:
            markdown += f"{norma}\n"
    
    markdown += f"\n**¿Qué hacer ahora?**\n{r.proxima_accion}\n"
    
    if r.advertencias:
        markdown += f"\n{r.advertencias}\n"
    
    markdown += f"""
---
*Consultado: {audit_response.metadata.get('agente_consultado', 'Sistema')}*
*Confianza: {int(audit_response.metadata.get('confianza', 0.95) * 100)}%*"""
    
    return {"markdown": markdown, "audit_response": audit_response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)