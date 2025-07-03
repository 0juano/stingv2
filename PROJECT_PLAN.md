# 🎯 Bureaucracy Oracle - Project Plan

## 📋 Overview
Building a multi-agent system to help navigate Argentine regulations (BCRA, Comex, Senasa) with intelligent routing and user-friendly responses.

## ✅ Completed Tasks

### Backend Infrastructure
- [x] Create microservices architecture with FastAPI
- [x] Build base agent template for all services
- [x] Implement Router service for query routing
- [x] Create BCRA agent (Central Bank regulations)
- [x] Create Comex agent (Foreign trade)
- [x] Create Senasa agent (Agricultural safety)
- [x] Build Auditor service for response validation
- [x] Create agents.yml configuration file
- [x] Set up Docker Compose orchestration
- [x] Create orchestrator.py for CLI testing
- [x] Create Makefile for easy development
- [x] Write comprehensive README documentation

### Testing Infrastructure
- [x] Create test_questions.json with 30 test cases
- [x] Build test_routing.py for routing accuracy testing
- [x] Run initial routing test (83.3% accuracy)
- [x] Fix BCRA routing issues (improved to 96.7% accuracy)
- [x] Create routing visualization HTML report
- [x] Test with 230 questions dataset

### Frontend Development
- [x] Build React frontend with Vite + TypeScript
- [x] Create terminal-style chat interface
- [x] Implement ASCII flow visualization
- [x] Add Doom 64 theme styling
- [x] Connect frontend to backend API
- [x] Always-visible processing flow diagram

### Multi-Agent Support (✨ NEW)
- [x] Implement parallel multi-agent routing
- [x] Update router to identify multiple relevant agents
- [x] Create orchestrator_multiagent.py for parallel processing
- [x] Modify auditor to merge responses from multiple agents
- [x] Update frontend to show multi-agent processing
- [x] Display which agents were consulted in responses

## 🚧 In Progress

### Testing & Analysis
- [ ] Create full test suite (test_suite.py) that tests complete flow
- [ ] Build performance analysis dashboard
- [ ] Create cost tracking report
- [ ] Test error handling and timeout scenarios

## 📅 Upcoming Tasks

### Frontend Enhancements
- [ ] Implement real-time streaming responses
- [ ] Add conversation history
- [ ] Show agent selection reasoning in UI
- [ ] Add response confidence indicators

### Advanced Features
- [ ] Response caching for common queries
- [ ] Query suggestions/autocomplete
- [ ] Export chat history
- [ ] Rate limiting
- [ ] User authentication (optional)

### Production Readiness
- [ ] Add comprehensive logging
- [ ] Implement monitoring (Prometheus/Grafana)
- [ ] Create deployment scripts
- [ ] Add health checks and auto-recovery
- [ ] Security audit
- [ ] Load testing

## 🐛 Known Issues

1. **BCRA Agent Timeout** - Some queries to BCRA timeout (Netflix payment example)
2. **Router Case Sensitivity** - Returns "BCRA" instead of "bcra"
3. ~~**Missing Multi-Agent Support** - Can only route to one agent at a time~~ ✅ FIXED
4. **No Error Recovery** - If one service fails, entire query fails

## 💡 Ideas & Improvements

- Add a "Confidence Score" to help users understand response reliability
- Implement a feedback mechanism to improve routing over time
- Create specialized prompts for edge cases (e.g., crypto regulations)
- Add support for follow-up questions
- Implement Spanish/English language detection
- Create a "learning mode" that explains regulations step-by-step

## 📊 Metrics to Track

- **Routing Accuracy**: 96.7% (improved from 83.3%)
- **Multi-Agent Detection**: 39.1% of queries need multiple agents
- **Average Response Time**: ~8 seconds (estimated)
- **Cost per Query**: ~$0.001-0.002
- **Success Rate**: TBD
- **User Satisfaction**: TBD

## 🎯 Next Immediate Actions

1. **[HIGH PRIORITY] Implement Tavily Search Integration** - Add real-time search capabilities
2. Test multi-agent queries with 230 question dataset
3. Create performance dashboard
4. Add streaming responses to frontend
5. Implement conversation history

## 🔍 Search Integration Plan (HIGH PRIORITY)

### Overview
Integrate Tavily Search API to provide real-time, up-to-date information for Argentine regulations, addressing the limitation of GPT-4o-mini's October 2023 knowledge cutoff.

### Architecture Design

#### 1. **Search Service Component**
Create a new shared search service that all agents can use:
```
agents/
  search_service.py  # New centralized search module
    - TavilySearchService class
    - search() method with rate limiting
    - parse_results() for formatting
    - cache_results() for cost optimization
```

#### 2. **Agent Integration Points**
Modify each agent's `answer()` function to:
1. Detect if search is needed (keywords: "actual", "hoy", "vigente", "último", "2024", "2025")
2. Call search service with agent-specific queries
3. Include search results in the LLM prompt context
4. Maintain existing response structure

#### 3. **Search Strategies by Agent**

##### BCRA Agent
Primary search domains and queries:
- **Official BCRA**: `site:bcra.gob.ar [query]`
- **Communications**: `"Comunicación A" BCRA 2024 [topic]`
- **Key searches**:
  - "límite pago servicios digitales BCRA 2024"
  - "cepo cambiario Argentina actual"
  - "dólar MEP CCL cotización hoy"
- **Specific sites**:
  - bcra.gob.ar/PublicacionesEstadisticas/Principales_variables.asp
  - bcra.gob.ar/Noticias/comunicados-bcra.asp

##### COMEX Agent
Primary search domains and queries:
- **AFIP/Customs**: `site:afip.gob.ar aduana [query]`
- **Trade Ministry**: `site:argentina.gob.ar comercio exterior [query]`
- **Key searches**:
  - "posición arancelaria NCM [product] Argentina"
  - "SIMI sistema importaciones Argentina 2024"
  - "arancel importación [product] Argentina actual"
- **Specific sites**:
  - tarifar.com (for NCM codes)
  - argentina.gob.ar/produccion/comercio-exterior

##### SENASA Agent
Primary search domains and queries:
- **Official SENASA**: `site:senasa.gob.ar [query]`
- **Phytosanitary**: `certificado fitosanitario [country] [product] Argentina`
- **Key searches**:
  - "requisitos exportación [product] [country] SENASA"
  - "protocolo sanitario Argentina [país] 2024"
  - "ROE registro exportadores SENASA"
- **Specific sites**:
  - senasa.gob.ar/consulta-de-requisitos-fitosanitarios
  - senasa.gob.ar/exportaciones

### Implementation Steps

#### Phase 1: Core Search Infrastructure (Week 1)
1. **Set up Tavily API**
   - Add TAVILY_API_KEY to environment variables
   - Create search_service.py with rate limiting
   - Implement result parsing and formatting

2. **Create Search Detection Logic**
   ```python
   def needs_search(question: str) -> bool:
       # Detect temporal keywords, specific rates, recent changes
       temporal_keywords = ["actual", "hoy", "vigente", "último", "2024", "2025"]
       rate_keywords = ["cotización", "tipo de cambio", "límite actual"]
       return any(keyword in question.lower() for keyword in temporal_keywords + rate_keywords)
   ```

3. **Implement Caching Layer**
   - Cache search results for 24 hours for rates/limits
   - Cache regulatory searches for 7 days
   - Use Redis or in-memory cache

#### Phase 2: Agent Integration (Week 1-2)
1. **Update Agent Prompts**
   Add to each agent's prompt.md:
   ```
   Cuando recibas resultados de búsqueda actualizados, úsalos para proporcionar información 
   actualizada. Siempre cita la fuente y fecha de la información encontrada.
   ```

2. **Modify Agent Processing**
   ```python
   async def answer(query: QueryRequest):
       # Existing code...
       
       # New: Check if search needed
       if needs_search(query.question):
           search_results = await search_service.search(
               query=query.question,
               agent_type=self.agent_name,
               domains=self.search_domains
           )
           
           # Include in prompt
           enhanced_question = f"""
           Pregunta: {query.question}
           
           Información actualizada encontrada:
           {format_search_results(search_results)}
           
           Por favor responde basándote en esta información actualizada.
           """
       
       # Continue with existing LLM call...
   ```

3. **Test Each Agent**
   - Create test queries requiring current information
   - Verify search results are properly integrated
   - Ensure response format remains consistent

#### Phase 3: Advanced Features (Week 2)
1. **Smart Search Triggers**
   - Implement ML-based detection for search needs
   - Learn from user queries over time
   - Optimize search queries based on success rates

2. **Multi-Source Aggregation**
   - Combine results from multiple sources
   - Rank by relevance and authority
   - Handle conflicting information

3. **Performance Optimization**
   - Parallel search requests
   - Pre-fetch common queries
   - Background updates for cached data

### Cost Estimation
- Tavily API: $0.004 per search
- Estimated searches per query: 0-2 (only when needed)
- With caching: ~$0.002 additional cost per query average
- Monthly estimate (10k queries): ~$20

### Testing Strategy
1. **Unit Tests**
   - Search service functionality
   - Result parsing
   - Cache behavior

2. **Integration Tests**
   - Each agent with search scenarios
   - Multi-agent queries with search
   - Error handling (API failures)

3. **Test Scenarios**
   ```
   BCRA: "¿Cuál es el límite actual para pagar Netflix desde Argentina?"
   COMEX: "¿Qué arancel tiene la importación de notebooks en 2024?"
   SENASA: "¿Requisitos vigentes para exportar limones a Europa?"
   Multi: "¿Cómo importar medicamentos y cuánto puedo pagar al proveedor?"
   ```

### Monitoring & Metrics
- Track search usage per agent
- Monitor cache hit rates
- Measure response time impact
- Track cost per query
- Log search failures and fallbacks

### Rollback Strategy
- Feature flag to enable/disable search
- Fallback to non-search responses
- Manual override for specific queries

---

Last Updated: 2025-01-03 08:45 ART