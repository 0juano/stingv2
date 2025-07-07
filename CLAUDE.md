# Bureaucracy Oracle - Project Documentation

## Standard Workflow
1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the todo.md file with a summary of the changes you made and any other relevant information.

## 🚨🚨🚨 CRITICAL: NEVER EXPOSE API KEYS 🚨🚨🚨

**NEVER, EVER put API keys in:**
- Any file that gets committed to Git
- Shell scripts (.sh files)
- Docker-compose files
- Documentation files
- ANY file except .env (which is gitignored)

**API keys should ONLY exist in:**
- `.env` file (which is in .gitignore)
- Environment variables on the server

**Before committing ANY file, check for:**
- Strings starting with `sk-or-`
- Strings starting with `tvly-`
- Any long random strings that look like keys

**If you accidentally expose a key:**
1. Remove it immediately
2. Commit the removal
3. The key is now compromised and must be replaced
4. User must create a new key at https://openrouter.ai/keys

## Overview
This is a 5-agent n8n workflow that acts as a bureaucracy oracle for Argentine regulations. It intelligently routes queries to specialized agents and provides formatted, actionable responses.

## Purpose & Scope
The Bureaucracy Oracle is designed to help users navigate Argentine regulations and bureaucratic processes. 

**The app helps users understand:**
- **HOW** to do things legally (procedures, steps, requirements)
- **WHAT** regulations apply to their situation
- **WHICH** documents are needed for procedures
- **WHERE** to do procedures (which offices, systems, websites)

**The app does NOT provide:**
- Live market data (exchange rates, stock prices)
- Real-time pricing information
- Data that changes minute by minute

The search feature (when enabled) focuses on finding **current regulations and procedures**, not current prices or rates.

## Architecture

### 1. **Switchboard Agent**
- Routes incoming queries to the appropriate specialized agent
- Determines if query is about BCRA, Comex, Senasa, or out of scope
- Uses GPT-4o-mini for cost efficiency

### 2. **Specialized Agents** (all use GPT-4o)
- **BCRA Agent**: Central Bank regulations (foreign payments, currency exchange, CEPO)
- **Comex Agent**: Foreign trade (imports/exports, tariffs, licenses)
- **Senasa Agent**: Agricultural/food safety and phytosanitary requirements

### 3. **Auditor/Summarizer Agent**
- Validates agent responses for accuracy and completeness
- Creates user-friendly summaries with emojis and clear structure
- Ensures citations are properly formatted

### 4. **Supporting Nodes**
- **Add Agent Name**: Captures agent output and adds metadata
- **Format Final Response**: Creates beautiful markdown responses
- **Debug Collector**: Captures full execution flow for troubleshooting

## Key Features
- Structured JSON output from all agents
- Automatic citation formatting
- Clear action items and next steps
- Debug mode for troubleshooting
- Handles out-of-scope queries gracefully

## Test Queries
See test_queries.md for sample queries to test each agent.

## Important Notes
- Always use main_clean.json for importing into n8n
- All agents expect questions about Argentine regulations
- Responses are limited to 250-300 words for clarity
- Citations use format: [Type Number/Year, article X]

## Troubleshooting
If agents return INSUFFICIENT_CONTEXT:
1. Check if the query is within the agent's domain
2. Ensure the query is specific enough
3. Review agent prompts for coverage gaps

## Language Requirements
- **IMPORTANT**: All agent responses MUST be in Spanish
- The UI text is in Spanish (except technical headers)
- This is a product for Argentina - all content should be in Spanish
- The backend agents should return Spanish responses

## Future Enhancements
- Add AFIP agent for tax regulations
- Add IGJ agent for corporate law
- Implement caching for frequently asked questions
- Add webhook for Slack/Discord integration

## Local vs Production Deployment

### Local Development
```bash
# docker-compose.override.yml is automatically loaded
docker-compose up --build
```

### Production Deployment  
```bash
# On the server, rename override file and use prod config
mv docker-compose.override.yml docker-compose.override.yml.bak
cp docker-compose.prod.yml docker-compose.override.yml
docker-compose up --build -d
```

## DigitalOcean/Docker Deployment Quirks

### Common Issues and Solutions

1. **docker-compose recreate container error: 'ContainerConfig'**
   - This happens when docker-compose tries to recreate a container
   - Solution: Force remove and recreate
   ```bash
   docker rm -f container_name
   docker-compose up -d service_name
   ```

2. **Frontend not accessible from other computers (Network Error)**
   - React/Vite environment variables are baked at BUILD time, not runtime
   - The `VITE_API_BASE_URL` must be set to the server IP, not localhost
   - Solution: Rebuild frontend with correct API URL
   ```bash
   docker build -t proyecto-sting_frontend \
     --build-arg VITE_API_BASE_URL=http://YOUR_SERVER_IP:8001 \
     --no-cache ./frontend
   ```

3. **Default directory on SSH**
   - Add to ~/.bashrc to auto-navigate to project:
   ```bash
   echo "cd /opt/proyecto-sting" >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Firewall blocks ports**
   - DigitalOcean Docker image only allows SSH (22) and Docker (2375/2376) by default
   - Open required ports:
   ```bash
   ufw allow 80
   ufw allow 8001
   ufw allow 8002
   ufw allow 8003
   ufw allow 8004
   ufw allow 8005
   ```

5. **Frontend Dockerfile needs ARG support**
   - Add these lines to accept build-time API URL:
   ```dockerfile
   ARG VITE_API_BASE_URL=http://localhost:8001
   ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
   ```

6. **docker-compose vs docker compose**
   - DigitalOcean uses older `docker-compose` (hyphenated)
   - Both work, but stick with `docker-compose` for consistency

7. **Check if services are using correct URLs**
   ```bash
   # Verify frontend has server IP in built files
   docker exec frontend grep -r "YOUR_SERVER_IP" /usr/share/nginx/html/assets/
   ```