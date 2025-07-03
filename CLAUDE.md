# Bureaucracy Oracle - Project Documentation

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