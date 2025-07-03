# 🏛️ Bureaucracy Oracle

A microservices-based intelligent assistant for navigating Argentine bureaucracy. Routes questions to specialized agents (BCRA, Comex, Senasa) and provides clear, actionable answers with legal citations.

## 📋 What This App Does

**✅ The app helps you understand:**
- **HOW** to do things legally (procedures, steps, requirements)
- **WHAT** regulations apply to your situation
- **WHICH** documents you need for procedures
- **WHERE** to complete procedures (offices, systems, websites)

**❌ The app does NOT provide:**
- Live market data (exchange rates, stock prices)
- Real-time pricing information
- Data that changes minute by minute

> 💡 **Example:** Ask "¿Cómo comprar dólar MEP legalmente?" not "¿Cuál es la cotización del dólar MEP?"

## 🚀 Quick Start

```bash
# 1. Clone and enter directory
cd bureaucracy-oracle

# 2. Set up environment
make setup
# Edit .env with your OpenRouter API key

# 3. Start all services
make dev

# 4. Test it out
python3 orchestrator.py "¿Cómo exportar aceitunas a Grecia?"
```

## 🛠️ Tech Stack

### Frontend
- **React 19** + TypeScript
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Lucide React** - Icons

### Backend
- **FastAPI** (Python) - Web framework
- **Docker Compose** - Container orchestration
- **Microservices Architecture** - 5 independent services

### AI/ML
- **OpenRouter API** - Model provider
- **GPT-4o-mini** - Router and agents
- **GPT-4o** - Auditor service
- **Tavily API** - Web search integration

### Development
- **Make** - Build automation
- **ESLint** - Frontend linting
- **Python** - Backend language

## 🏗️ Architecture

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

### Services

- **Router (Port 8001)**: Analyzes queries and routes to appropriate agent
- **BCRA Agent (Port 8002)**: Central Bank regulations, foreign payments
- **Comex Agent (Port 8003)**: Import/export, trade regulations
- **Senasa Agent (Port 8004)**: Agricultural safety, phytosanitary certificates
- **Auditor (Port 8005)**: Validates responses and formats for users

## 📁 Project Structure

```
bureaucracy-oracle/
├── agents/
│   ├── base_agent.py      # Shared template for all agents
│   ├── router/            # Query routing service
│   ├── bcra/              # Central Bank agent
│   ├── comex/             # Foreign trade agent
│   ├── senasa/            # Agricultural safety agent
│   └── auditor/           # Response validator/formatter
├── agents.yml             # Agent configuration
├── docker-compose.yml     # Service orchestration
├── orchestrator.py        # CLI tool for testing
├── Makefile              # Development commands
└── .env                  # API keys (create from .env.example)
```

## 🛠️ Development

### Available Commands

```bash
make dev        # Start all services with hot reload
make logs       # View logs from all services
make test       # Run test query
make down       # Stop all services
make clean      # Clean up containers and images
```

### Testing Individual Services

```bash
# Test router
make test-router

# Test specific agent
make test-comex
make test-bcra
make test-senasa

# Check service health
make test-health
```

### Adding a New Agent

1. Copy the template:
```bash
cp -r agents/bcra agents/newagent
```

2. Update the prompt:
```bash
vim agents/newagent/prompt.md
```

3. Add to `agents.yml`:
```yaml
- slug: newagent
  name: Agente Nuevo
  endpoint: http://newagent:8000
  color: "#color"
  icon: "🆕"
```

4. Add to `docker-compose.yml`:
```yaml
newagent:
  build: ./agents/newagent
  container_name: newagent
  ports:
    - "8006:8000"
  environment:
    - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    - AGENT_NAME=newagent
  networks:
    - oracle-network
```

5. Restart services:
```bash
make dev
```

## 🔧 Configuration

### Environment Variables

Create `.env` from `.env.example`:
```bash
OPENROUTER_API_KEY=your_key_here
TAVILY_API_KEY=your_tavily_key_here
ENABLE_SEARCH=true
```

### Agent Configuration

Edit `agents.yml` to:
- Add/remove agents
- Change agent colors and icons
- Update agent descriptions

### Model Selection

Default models (can override in docker-compose.yml):
- Router: `openai/gpt-4o-mini` (cost-efficient)

## 🚀 Railway Deployment

### Quick Deploy

1. **Set up Railway account and install CLI:**
```bash
npm install -g @railway/cli
railway login
```

2. **Deploy with our automation script:**
```bash
./infra/railway.sh <your-project-id>
```

3. **Configure environment variables in Railway dashboard:**
- `OPENROUTER_API_KEY`
- `TAVILY_API_KEY`
- `ENABLE_SEARCH=true`

### GitHub Actions CI/CD

The project includes automated deployment:
- Push to `main` → Automatic deployment
- Tag `v*` → Production release
- All tests must pass (≥90% coverage)

### Monitoring & Performance

```bash
# Check latency from Buenos Aires
./scripts/ping-buenos-aires.sh

# Monitor costs (runs daily)
./scripts/cost-monitor.py

# Health check all services
./scripts/health-check-all.sh
```

### Production URLs
- Frontend: `https://bureaucracy-oracle.up.railway.app`
- API Router: `https://router.up.railway.app`
- Health Dashboard: Railway project dashboard

### Cost Optimization
- Auto-sleep after 10 minutes idle
- Target: <$20/month on Hobby plan
- Monitor with `cost-monitor.py`

### Performance Targets
- Average RTT from Buenos Aires: <170ms
- p95 API response time: <500ms
- Multi-agent queries: <8s
- Agents: `openai/gpt-4o-mini`
- Auditor: `openai/gpt-4o` (higher quality for final formatting)

## 💰 Cost Tracking

The system tracks OpenRouter API costs:
- Each service reports its cost via headers
- Orchestrator aggregates total cost
- Displayed after each query

Example output:
```
💰 Total cost: $0.0024
```

## 🧪 API Reference

### Router Service

```bash
POST /route
{
  "question": "¿Cómo exportar aceitunas?"
}

Response:
{
  "decision": {
    "agent": "comex",
    "reason": "Consulta sobre exportación",
    "confidence": 0.95
  },
  "agents_available": ["bcra", "comex", "senasa"],
  "cost": 0.0001
}
```

### Agent Services

```bash
POST /answer
{
  "question": "¿Cómo exportar aceitunas a Grecia?"
}

Response:
{
  "answer": {
    "Respuesta": "Para exportar aceitunas...",
    "Normativa": [...],
    "PasosRequeridos": [...]
  },
  "agent": "comex",
  "model": "openai/gpt-4o-mini",
  "cost": 0.0008
}
```

### Auditor Service

```bash
POST /audit
{
  "user_question": "...",
  "agent_response": {...},
  "agent_name": "comex"
}

Response:
{
  "status": "Aprobado",
  "motivo_auditoria": "Respuesta completa y precisa",
  "respuesta_final": {
    "titulo": "🎯 Exportación de Aceitunas",
    "respuesta_directa": "✅ Puede exportar...",
    "detalles": [...],
    "normativa_aplicable": [...],
    "proxima_accion": "👉 Registrarse en AFIP"
  },
  "metadata": {...},
  "cost": 0.0015
}
```

## 🚢 Deployment Options

### Local Development

```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Railway (Recommended)

See [Railway Deployment](#-railway-deployment) section above for detailed instructions.

### Other Platforms

- **Render**: Good Docker support, free tier available
- **Fly.io**: Excellent for global distribution
- **DigitalOcean App Platform**: Enterprise-ready but more expensive

## 🐛 Troubleshooting

### Services not starting
```bash
# Check logs
make logs

# Verify .env exists
cat .env

# Test individual service
make logs-router
```

### High costs
- Switch to cheaper models in docker-compose.yml
- Reduce temperature in agent code
- Cache frequent queries

### Slow responses
- Check OpenRouter status
- Verify network connectivity
- Consider using faster models

## 📈 Future Enhancements

- [ ] Frontend with React + React-Flow
- [ ] Query caching with Redis
- [ ] Response streaming
- [ ] Multi-agent queries
- [ ] Historical query tracking
- [ ] A/B testing different prompts

## 📄 License

MIT License - See LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

Built with ❤️ for navigating Argentine bureaucracy