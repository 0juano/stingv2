# Bureaucracy Oracle - Complete Project Overview

## 🎯 Project Purpose & Scope

**Bureaucracy Oracle** is a microservices-based intelligent assistant designed to help users navigate Argentine bureaucracy. It routes questions to specialized agents and provides clear, actionable answers with legal citations.

### What This App Does ✅
- **HOW** to do things legally (procedures, steps, requirements)
- **WHAT** regulations apply to specific situations
- **WHICH** documents are needed for procedures
- **WHERE** to complete procedures (offices, systems, websites)

### What This App Does NOT Do ❌
- Live market data (exchange rates, stock prices)
- Real-time pricing information
- Data that changes minute by minute

### Language Requirements 🇦🇷
- **All agent responses MUST be in Spanish**
- UI text is in Spanish (except technical headers)
- This is a product for Argentina - all content in Spanish

## 🏗️ Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Router    │────▶│    BCRA     │
│  (React)    │     │  (8001)     │     │   (8002)    │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │                    
                           │             ┌─────────────┐
                           ├────────────▶│    Comex    │
                           │             │   (8003)    │
                           │             └─────────────┘
                           │                    
                           │             ┌─────────────┐
                           └────────────▶│   Senasa    │
                                        │   (8004)    │
                                        └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Auditor   │
                                        │   (8005)    │
                                        └─────────────┘
```

### Services & Responsibilities

1. **Router (Port 8001)** - GPT-4o-mini
   - Analyzes queries and routes to appropriate agent
   - Handles multi-agent queries
   - Confidence scoring for routing decisions

2. **BCRA Agent (Port 8002)** - GPT-4o
   - Central Bank regulations
   - Foreign payments, currency exchange (CEPO)
   - Import payment regulations (SIRA, SIRASE)

3. **Comex Agent (Port 8003)** - GPT-4o
   - Import/export procedures
   - Trade regulations, tariffs
   - Customs classifications (NCM codes)

4. **Senasa Agent (Port 8004)** - GPT-4o
   - Agricultural safety
   - Phytosanitary certificates
   - Food safety standards

5. **Auditor (Port 8005)** - GPT-4o
   - Validates agent responses
   - Formats for user consumption
   - Adds emojis and structure

## 🔄 Query Processing Flow

```python
# Orchestrator flow (orchestrator.py)
1. Router analyzes query → determines agent(s)
2. Selected agent(s) process query (with optional web search)
3. Auditor validates and formats response
4. Frontend displays formatted response with flow visualization
```

## 📝 Core Agent Prompts

### Router Agent
```json
// Routes queries based on domain expertise
{
    "agents": ["bcra", "comex"],
    "primary_agent": "bcra",
    "reason": "Query about import payments requires BCRA approval",
    "confidence": 0.85
}
```

### Specialized Agent Response Format
```json
{
  "Respuesta": "Para exportar productos alimenticios...",
  "Normativa": [
    {"tipo": "Ley", "número": "22.415", "artículo": "332", "año": "1981"}
  ],
  "PasosRequeridos": ["Inscripción AFIP", "Clasificación NCM"],
  "DocumentacionNecesaria": ["Factura E", "Certificado SENASA"],
  "NCM": "Capítulos 01-24",
  "ArancelExportacion": "0-33%",
  "confidence": 0.90,
  "confidence_factors": {
    "has_specific_regulations": true,
    "has_exact_articles": true,
    "has_complete_procedures": true
  }
}
```

### Auditor Output Format
```json
{
  "status": "Aprobado",
  "motivo_auditoria": "Respuesta completa y precisa",
  "respuesta_final": {
    "titulo": "🎯 Exportación de Aceitunas",
    "respuesta_directa": "✅ Puede exportar siguiendo estos pasos...",
    "detalles": [
      "📌 Inscribirse como exportador en AFIP",
      "📌 Obtener certificado fitosanitario de SENASA"
    ],
    "normativa_aplicable": [
      "📋 [Código Aduanero Ley 22.415, art. 332]",
      "📋 [Res. SC 26/2024, art. 2]"
    ],
    "proxima_accion": "👉 Registrarse en el sistema AFIP"
  },
  "metadata": {
    "agente_consultado": "comex",
    "confianza": 0.85,
    "busquedas_web": 2
  },
  "cost": 0.0024
}
```

## 🔍 Search Integration (Tavily)

```python
# Search service integration (agents/search_service.py)
class TavilySearchService:
    def needs_search(self, question: str, agent_type: str) -> str:
        # Returns: "none", "quick", or "full"
        # Based on temporal triggers and topic complexity
        
    async def search(self, query: str, agent_type: str) -> Dict:
        # Performs web search with agent-specific optimization
        # Caches results for 15 minutes (regulations) or 1 hour (rates)
```

### Cost Tracking
```python
# Cost calculation (agents/cost_calculator.py)
PRICING = {
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},  # per million tokens
    "openai/gpt-4o": {"input": 5.00, "output": 15.00}
}
TAVILY_BASIC_COST = 0.004   # Quick search
TAVILY_SEARCH_COST = 0.015  # Advanced search
```

## 🎨 Frontend Architecture

### Terminal-Style React Component
```typescript
// TerminalSimple.tsx - Main UI component
interface Message {
  id: string;
  type: 'user' | 'system' | 'response';
  content: string;
  timestamp: Date;
  flow?: any;
  cost?: number;
  duration?: number;
}

// Real-time flow visualization with Framer Motion
<FlowDiagramSimple 
  flow={currentFlow} 
  isProcessing={isProcessing}
/>
```

## 🛠️ Key Design Patterns

### 1. FastAPI Service Structure
```python
# Base agent template (base_agent.py)
app = FastAPI(title="Agent Service")

class QueryRequest(BaseModel):
    question: str
    context: Dict[str, Any] = Field(default_factory=dict)

class QueryResponse(BaseModel):
    answer: Dict[str, Any]
    agent: str
    model: str
    cost: float = 0.0
    error: Optional[str] = None

@app.post("/answer", response_model=QueryResponse)
async def answer_question(query: QueryRequest):
    # 1. Load prompt
    # 2. Optional: Perform web search
    # 3. Call OpenRouter API
    # 4. Calculate costs (LLM + search)
    # 5. Return structured response
```

### 2. Confidence Scoring System
```python
# Agent confidence calculation
confidence = 0.5  # Base
confidence += 0.2  # Specific regulations cited
confidence += 0.15  # Exact articles referenced
confidence += 0.1  # Complete procedures described
confidence += 0.05  # NCM codes included
confidence += 0.05  # Tariff rates specified
```

### 3. Multi-Agent Query Handling
```python
# Router can select multiple agents
{
    "agents": ["senasa", "comex", "bcra"],
    "primary_agent": "senasa",
    "reason": "Exportación de alimentos requiere SENASA (sanidad), COMEX (procedimientos), BCRA (divisas)"
}
```

## 📊 Response Quality Metrics

### Confidence Breakdown Display
```
📊 **Desglose de confianza:**
Puntuación base:         50 / 50 ✓
Regulaciones específicas:17 / 20 ✗
Artículos exactos:       13 / 15 ✗
Procedimientos completos: 8 / 10 ✗
Actualizaciones recientes: 4 / 5 ✗
────────────────────────────────────────
Total:                   85 / 100

💰 **Costo de búsquedas web:**
Búsquedas realizadas:    2
Costo Tavily:            $0.0190
```

## 🚀 Development Workflow

```bash
# Development commands (Makefile)
make dev        # Start all services with hot reload
make logs       # View logs from all services
make test       # Run test query
make down       # Stop all services

# Service health checks
curl http://localhost:8001/health  # Router
curl http://localhost:8002/health  # BCRA
curl http://localhost:8003/health  # Comex
curl http://localhost:8004/health  # Senasa
curl http://localhost:8005/health  # Auditor
```

## 🔐 Environment Configuration

```bash
# .env file
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o  # Can override per service
ENABLE_SEARCH=true
TAVILY_API_KEY=your_tavily_key
```

## 📝 Code Style Guidelines

### Python (Backend)
- FastAPI with Pydantic models for validation
- Async/await for all HTTP calls
- Structured JSON responses
- Cost tracking on every API call
- Spanish language for all user-facing content

### TypeScript/React (Frontend)
- Functional components with hooks
- Tailwind CSS for styling
- Framer Motion for animations
- Terminal-style monospace UI
- Real-time flow visualization

### Response Formatting
- Always include confidence scores
- Use emojis for visual hierarchy
- Cite regulations in format: [Type Number/Year, art. X]
- Structure: Title → Direct Answer → Details → Next Steps
- Track and display all costs (LLM + search)

## 🎯 Key Features

1. **Intelligent Routing** - Queries go to the right expert
2. **Multi-Agent Support** - Complex queries use multiple agents
3. **Web Search Integration** - Real-time regulation updates
4. **Cost Tracking** - Transparent pricing per query
5. **Confidence Scoring** - Quality metrics for responses
6. **Structured Output** - Consistent JSON formatting
7. **Spanish Language** - All responses in Spanish
8. **Visual Flow** - See the decision process
9. **Citation Formatting** - Legal references included
10. **Error Handling** - Graceful fallbacks

## 🔮 Future Enhancements

- Add AFIP agent for tax regulations
- Add IGJ agent for corporate law
- Implement Redis caching
- Add webhook integrations
- Response streaming
- A/B testing for prompts