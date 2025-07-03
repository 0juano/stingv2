# Confidence Score Implementation

## Overview
Implemented real confidence scoring for agent responses instead of hardcoded 95%.

## Changes Made

### 1. Agent Prompts Updated
- **SENASA** (`agents/senasa/prompt.md`): Added confidence calculation
- **BCRA** (`agents/bcra/prompt.md`): Added confidence calculation  
- **Comex** (`agents/comex/prompt.md`): Added confidence calculation

Each agent now returns:
```json
{
  "confidence": 0.0-1.0,
  "confidence_factors": {
    "has_specific_regulations": true/false,
    "has_exact_articles": true/false,
    "has_complete_procedures": true/false,
    "has_recent_updates": true/false,
    "contains_insufficient_context": true/false
  }
}
```

### 2. Confidence Calculation Formula
```
Base confidence: 0.5
+0.2 if specific regulations/communications cited
+0.15 if exact articles/points included
+0.1 if complete procedures described
+0.05 if recent updates referenced
Maximum 0.2 if INSUFFICIENT_CONTEXT
```

### 3. Auditor Updates (`agents/auditor/main.py`)
- Extracts confidence from agent responses
- For single agent: uses agent's confidence
- For multi-agent: uses primary agent's confidence
- Default: 0.85 if no confidence available

### 4. Final Formatter Updates (`updated_formatter.js`)
- Removed hardcoded `|| 0.95` default
- Only displays confidence if available
- Adds explanation for low confidence (<80%)
- Examples:
  - "Confianza: 65% (sin regulaciones específicas)"
  - "Confianza: 20% (información limitada disponible)"

## Benefits
1. **Transparency**: Users see actual confidence based on response quality
2. **Reliability**: Low confidence warns users to seek additional information
3. **Accuracy**: Reflects actual completeness of the answer

## Testing
Use `test_confidence.py` to verify calculations:
- High confidence (85-95%): Complete answers with specific citations
- Medium confidence (60-80%): General information, missing specifics
- Low confidence (<60%): Incomplete or insufficient context

## Next Steps for n8n Workflow
Replace the "Format Final Response" node's JavaScript code with the content from `updated_formatter.js` to enable dynamic confidence display.