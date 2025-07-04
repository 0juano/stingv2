---

kanban-plugin: board

---

## 📋 Backlog

### Quick Wins (This Weekend)
- [ ] **Get a domain name** ($1-10) - oraculo.xyz or burocracia.app
- [ ] **Add basic analytics** - Track queries, agent usage, visitor origins
- [ ] **Share with 5 test users** - Post in Argentina Reddit/Discord/WhatsApp
- [ ] **Add "Examples" button** - Show common queries users can try

### Next Week Improvements
- [ ] **Monitor API costs daily** - Add cron job for cost-monitor.py
- [ ] **Add error recovery** - Handle OpenRouter downtime gracefully
- [ ] **Cache common queries** - Save API costs on repeated questions
- [ ] **Improve error messages** - User-friendly messages in Spanish

### Growth Features
- [ ] **Create landing page** - Explain what the oracle does
- [ ] **Add share buttons** - Let users share helpful responses
- [ ] **Implement feedback system** - "¿Fue útil? 👍👎"
- [ ] **Make mobile PWA** - Add to home screen capability
- [ ] **Add visitor counter** - Show "X consultas respondidas"



## Future Features

- [ ] Add links to normativa documents when shared
- [ ] Implement real-time streaming responses
- [ ] Add conversation history
- [ ] Show agent selection reasoning in UI
- [ ] Response caching for common queries
- [ ] Query suggestions/autocomplete
- [ ] Export chat history
- [ ] Rate limiting
- [ ] User authentication (optional)


## Testing & Quality

- [ ] Create comprehensive test suite
- [ ] Test multi-agent with 230 questions
- [ ] Performance benchmarking
- [ ] Test error handling scenarios
- [ ] Load testing
- [ ] Security audit


## DevOps & Monitoring

- [ ] Add comprehensive logging
- [ ] Implement monitoring (Prometheus/Grafana)
- [ ] Create automated deployment scripts
- [ ] Add health checks and auto-recovery
- [ ] **Add HTTPS with Let's Encrypt** 🔒
- [ ] **Get cheap domain name** (namecheap ~$1/year for .xyz)


## 🚧 In Progress



## 🧪 Testing/Review



## ✅ Done

## Deployment & Production

- [x] **Deploy to DigitalOcean** 🚀
	  - [x] Set up Docker 1-Click Droplet ($12/month)
	  - [x] Configure all 6 services with Docker Compose
	  - [x] Set up environment variables
	  - [x] Configure firewall rules
	  - [x] Deploy at http://147.182.248.187
	  - [x] Add favicon and Spanish title
	  - [x] Update header to "ORÁCULO DE LA BUROCRACIA"
	  **Completed**: July 4, 2025 - Live in production!

## Core Infrastructure

- [x] Create microservices architecture with FastAPI
- [x] Build base agent template for all services
- [x] Set up Docker Compose orchestration
- [x] Create Makefile for easy development


## Agents & Services

- [x] Implement Router service for query routing (96.7% accuracy)
- [x] Create BCRA agent (Central Bank regulations)
- [x] Create Comex agent (Foreign trade)
- [x] Create Senasa agent (Agricultural safety)
- [x] Build Auditor service for response validation
- [x] **Multi-agent queries** (parallel processing) 🎉


## Search Integration

- [x] **[HIGH PRIORITY] Complete Tavily Search Integration** 🔍 ^b3nkar
	  - [x] Create search_service.py module ✅
	  - [x] Add search detection logic ✅ (two-tier system)
	  - [x] Integrate with BCRA agent ✅
	  - [x] Integrate with COMEX agent ✅ 
	  - [x] Integrate with SENASA agent ✅
	  - [x] Add caching layer ✅
	  - [x] Implement two-tier search (quick + full) ✅
	  - [x] Add search metadata tracking ✅
	  - [x] Show search usage in responses ✅
	  **Notes**: All agents now have search capability with intelligent depth selection. Quick search ($0.004) for all queries, upgraded to full search ($0.015) for priority categories like import/export/arancel/límite/requisito.


## Frontend & UI

- [x] **Build React frontend with chat interface** 🎉
- [x] Create terminal-style UI with ASCII flow
- [x] Display which agents were consulted
- [x] **Add response confidence indicators** (shown as percentages)
- [x] Show search usage in all responses
- [x] Display search costs when applicable


## Testing & Documentation

- [x] Write comprehensive README documentation
- [x] Create test_questions.json with 30 test cases
- [x] Build test_routing.py for routing accuracy testing
- [x] Create routing visualization HTML report
- [x] Test with 230 questions dataset
- [x] **Run A/B Test with Real Questions** (search improves accuracy)


## Performance & Cost Tracking

- [x] **Implement cost tracking** (shown in each response)
- [x] Two-tier search system for cost optimization
- [x] Search caching to reduce API calls


## 🐛 Known Issues

- [ ] **BCRA Agent Timeout** - Some payment queries may timeout
- [ ] **No Error Recovery** - Cascading failures in multi-agent queries
- [ ] **Search sometimes returns incorrect data** - Need prompt refinement


## 💡 Ideas

- [x] ~~Add Confidence Score to responses~~ ✅ DONE
- [ ] Implement feedback mechanism
- [ ] Create specialized crypto regulation prompts
- [ ] Add follow-up question support
- [ ] Spanish/English language detection
- [ ] Create "learning mode" for regulations
- [ ] Add voice input/output
- [ ] Mobile app version


## ❓ Resolved Questions

- [x] **Q: Are agents properly compartmentalized?**
	  **A: Yes!** Each agent runs in its own Docker container with independent code, prompts, and configuration. Easy to modify individual agents without affecting others.




%% kanban:settings
```
{"kanban-plugin":"board","new-card-insertion-method":"prepend-compact","show-checkboxes":true,"archive-with-date":false,"list-collapse":[false,null,null,null,null,null]}
```
%%