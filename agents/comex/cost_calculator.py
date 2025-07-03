"""Cost calculator for OpenRouter API usage"""

# Tavily Search API pricing
TAVILY_SEARCH_COST = 0.015  # $0.015 per advanced search
TAVILY_BASIC_COST = 0.004   # $0.004 per basic search (approximate)

# Pricing per million tokens (as of January 2025)
PRICING = {
    "openai/gpt-4o-mini": {
        "input": 0.15,   # $0.15 per million tokens
        "output": 0.60   # $0.60 per million tokens
    },
    "openai/gpt-4o": {
        "input": 5.00,   # $5.00 per million tokens
        "output": 15.00  # $15.00 per million tokens
    },
    # Add more models as needed
}

def calculate_cost(model: str, usage: dict) -> float:
    """
    Calculate cost based on model and usage data
    
    Args:
        model: The model name (e.g., "openai/gpt-4o-mini")
        usage: Usage dict with prompt_tokens and completion_tokens
        
    Returns:
        Cost in dollars
    """
    if model not in PRICING:
        # Default to gpt-4o-mini pricing if model not found
        model = "openai/gpt-4o-mini"
    
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    
    # Calculate cost (price is per million tokens)
    input_cost = (prompt_tokens / 1_000_000) * PRICING[model]["input"]
    output_cost = (completion_tokens / 1_000_000) * PRICING[model]["output"]
    
    return input_cost + output_cost