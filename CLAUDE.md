# Bureaucracy Oracle - Project Documentation

## Overview
This is a 5-agent n8n workflow that acts as a bureaucracy oracle for Argentine regulations. It intelligently routes queries to specialized agents and provides formatted, actionable responses.

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

## Future Enhancements
- Add AFIP agent for tax regulations
- Add IGJ agent for corporate law
- Implement caching for frequently asked questions
- Add webhook for Slack/Discord integration