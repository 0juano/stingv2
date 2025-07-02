---

kanban-plugin: basic

---

## 📋 Backlog

- [ ] Build React frontend with chat interface
- [ ] Implement real-time streaming responses
- [ ] Add conversation history
- [ ] Create loading states and error handling
- [ ] Implement React-Flow for query routing visualization
- [ ] Show agent selection reasoning
- [ ] Display cost per query
- [ ] Add response confidence indicators
- [ ] Multi-agent queries (route to multiple agents)
- [ ] Response caching for common queries
- [ ] Query suggestions/autocomplete
- [ ] Export chat history
- [ ] Rate limiting
- [ ] User authentication (optional)
- [ ] Add comprehensive logging
- [ ] Implement monitoring (Prometheus/Grafana)
- [ ] Create deployment scripts
- [ ] Add health checks and auto-recovery
- [ ] Security audit
- [ ] Load testing

## 🚧 In Progress

- [ ] **Fix BCRA routing issues** 🔥
  - Q106, Q111, Q115 incorrectly routed to Comex
  - Q113 marked as out_of_scope
  - Q112 returns uppercase "BCRA"
- [ ] **Improve router prompt** 🔥
  - BCRA: Currency, payments, MULC, SIRA, financial regulations
  - Comex: Import/export procedures, tariffs, customs
  - When both apply: Financial → BCRA, Trade → Comex
- [ ] Create full test suite (test_suite.py)
- [ ] Build performance analysis dashboard
- [ ] Create cost tracking report
- [ ] Test error handling and timeout scenarios

## 🧪 Testing/Review

- [ ] Run full test suite on all 30 questions
- [ ] Verify routing accuracy improvements (target >90%)
- [ ] Performance benchmarking

## ✅ Done

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
- [x] Create test_questions.json with 30 test cases
- [x] Build test_routing.py for routing accuracy testing
- [x] Run initial routing test (83.3% accuracy)

## 🐛 Known Issues

- [ ] **BCRA Agent Timeout** - Netflix payment queries
- [ ] **Router Case Sensitivity** - Returns "BCRA" not "bcra"
- [ ] **Missing Multi-Agent Support** - Single agent only
- [ ] **No Error Recovery** - Cascading failures

## 💡 Ideas

- [ ] Add Confidence Score to responses
- [ ] Implement feedback mechanism
- [ ] Create specialized crypto regulation prompts
- [ ] Add follow-up question support
- [ ] Spanish/English language detection
- [ ] Create "learning mode" for regulations


%% kanban:settings
```
{"kanban-plugin":"basic","new-card-insertion-method":"prepend-compact","show-checkboxes":true,"archive-with-date":false}
```
%%