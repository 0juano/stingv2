# The Bureaucracy Oracle: Complete Logic Breakdown

## Core Mission
Create an intelligent assistant that helps people navigate Argentine bureaucracy by automatically routing questions to specialized regulatory experts and providing clear, actionable answers with proper legal citations.

## The Problem We're Solving
Argentine regulations are complex, scattered across multiple agencies, and written in legal jargon. Citizens need to know:
- How to pay for Netflix from Argentina (BCRA domain)
- How to export olives to Greece (Comex domain)  
- What certificates are needed for food exports (Senasa domain)
- And they need answers that are accurate, cited, and actionable

## The 5-Agent Architecture

### 1. The Receptionist: Chat Trigger
- **Purpose**: Receives user questions via chat interface
- **Logic**: Simple webhook that captures any text input from users
- **Output**: Passes raw user query to the Switchboard

### 2. The Traffic Controller: Switchboard Agent
- **Purpose**: Intelligent routing system that analyzes queries
- **Logic**: 
  - Uses GPT-4o-mini (cost-efficient) to understand the query topic
  - Has a structured output parser that forces JSON format
  - Makes one decision: Which expert should handle this?
- **Decision Tree**:
  - Currency/payments/foreign exchange → BCRA
  - Import/export/trade → Comex
  - Food safety/agricultural → Senasa
  - Everything else → FueraDeAlcance (out of scope)
- **Output**: `{"destinos": ["BCRA"], "razon": "Foreign payment query"}`

### 3. The Domain Experts: Specialized Agents
Three parallel branches, each with identical structure but different expertise:

#### BCRA Agent (Central Bank)
- **Domain**: Foreign payments, currency exchange, capital controls (CEPO)
- **Sources**: Central Bank communications ("A", "B", "C"), national laws
- **Logic**: 
  - Receives user's original question
  - Searches its "knowledge" of regulations
  - Formats response with specific requirements, limits, procedures
  - Includes legal citations in brackets
- **Output**: JSON with explanation and normative references

#### Comex Agent (Foreign Trade)
- **Domain**: Import/export procedures, tariffs, licenses
- **Sources**: Customs Code, Commerce Secretary resolutions
- **Special Logic**: Never says "insufficient context" for general export queries
- **Output**: Step-by-step export/import requirements with citations

#### Senasa Agent (Agricultural Safety)
- **Domain**: Phytosanitary certificates, food safety, animal health
- **Sources**: Senasa resolutions, Food Code
- **Output**: Health and safety requirements with legal backing

### 4. The Quality Controller: Add Agent Name Node
- **Purpose**: Data enrichment and error handling
- **Logic**:
  - Captures which agent actually processed the request
  - Extracts the agent's response (handles various formats)
  - Adds metadata for tracking
  - Provides fallback if agent fails
- **Output**: Standardized data package for the Auditor

### 5. The Editor-in-Chief: Auditor/Summarizer Agent
- **Purpose**: Quality control and user-friendly formatting
- **Dual Mission**:
  1. **Audit**: Verify response accuracy, completeness, proper citations
  2. **Summarize**: Transform technical response into beautiful, actionable format
- **Logic**:
  - Receives: user query + agent response + agent name
  - Validates response structure and content
  - Creates structured summary with:
    - 🎯 Clear title
    - ✅ Direct 1-2 sentence answer
    - 📌 Bullet points with key requirements
    - 📋 List of applicable laws
    - 👉 Immediate next action
    - ⚠️ Critical warnings
- **Output**: Structured JSON with approval status and formatted response

### 6. The Presenter: Format Final Response
- **Purpose**: Convert JSON to beautiful markdown
- **Logic**:
  - Takes Auditor's structured output
  - Builds user-friendly response with proper formatting
  - Handles different statuses (Approved/Observed/Rejected)
  - Adds metadata footer
- **Output**: Final markdown-formatted response

### 7. The Chronicler: Debug Collector
- **Purpose**: Complete execution tracking for troubleshooting
- **Logic**:
  - Captures entire execution flow
  - Safely handles JSON parsing errors
  - Creates both structured and human-readable debug reports
- **Output**: User response + complete debug information

## The Complete Flow

1. **User asks**: "How do I export olives to Greece?"
2. **Switchboard analyzes**: "This is about exports" → Routes to Comex
3. **Comex agent responds**: Lists requirements with legal citations
4. **Add Agent Name**: Captures response, adds "Comex" label
5. **Auditor reviews**: Validates accuracy, creates beautiful summary
6. **Formatter presents**: Converts to markdown with emojis
7. **Debug captures**: Records everything for analysis

## Key Design Decisions

### Why Multiple Agents?
- Specialization ensures accuracy
- Parallel processing for efficiency
- Easy to add new domains later

### Why Structured Output?
- Prevents hallucination
- Ensures consistent format
- Enables reliable parsing

### Why Audit Step?
- Quality control
- Transforms technical → user-friendly
- Adds trust through verification

### Why Debug Collector?
- Troubleshooting complex flows
- Performance optimization
- User feedback incorporation

## Error Handling

- **Out of scope**: Graceful message explaining limitations
- **Insufficient context**: Asks for more specific information
- **Agent failure**: Fallback error messages
- **Parse errors**: Safe string handling throughout

## The Innovation

This isn't just a chatbot—it's a **bureaucracy navigation system** that:
- Understands context and routes intelligently
- Speaks authoritatively with legal backing
- Transforms legalese into actionable steps
- Maintains accountability through citations
- Learns from failures through debug tracking

The beauty is in the **separation of concerns**: each agent does one thing excellently, and the combination creates an experience that feels magical to users while maintaining the accuracy required for legal/regulatory guidance.