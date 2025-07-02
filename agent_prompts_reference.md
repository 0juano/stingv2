# Agent Prompts Quick Reference

## Switchboard Agent
- Routes to: BCRA, Comex, Senasa, or FueraDeAlcance
- Output: `{"destinos": ["agent"], "razon": "brief explanation"}`

## BCRA Agent
**Domain**: Currency exchange, foreign payments, CEPO, debt registration
**Key Sources**: Communications "A", "B", "C" from BCRA, national laws
**Output Format**:
```json
{
  "Respuesta": "explanation with citations",
  "Normativa": [
    {"tipo": "Com. A", "número": "7825", "punto": "3.5", "año": "2023"}
  ]
}
```

## Comex Agent
**Domain**: Import/export, tariffs, licenses, NCM classification
**Key Sources**: Customs Code (Law 22.415), Commerce Secretary resolutions
**Special Instructions**: Always provide general export/import steps, don't return INSUFFICIENT_CONTEXT for standard queries
**Output Format**:
```json
{
  "Respuesta": "explanation with citations",
  "Normativa": [
    {"tipo": "Ley", "número": "22.415", "artículo": "489", "año": "1981"}
  ]
}
```

## Senasa Agent
**Domain**: Agricultural safety, phytosanitary requirements, food quality
**Key Sources**: Senasa resolutions, Food Code, official bulletins
**Output Format**: Same JSON structure as others

## Auditor/Summarizer
**Input**: User query + agent response + agent name
**Output**:
```json
{
  "status": "Aprobado|Observado|Rechazado",
  "motivo_auditoria": "max 20 words",
  "respuesta_final": {
    "titulo": "🎯 Descriptive title",
    "respuesta_directa": "✅ Essential answer in 1-2 sentences",
    "detalles": ["📌 key point 1", "📌 key point 2"],
    "normativa_aplicable": ["📋 Law/Regulation with year"],
    "proxima_accion": "👉 What to do now",
    "advertencias": "⚠️ Critical warnings if any"
  },
  "metadata": {
    "agente_consultado": "agent name",
    "confianza": 0.95
  }
}
```