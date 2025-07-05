# OpenRouter API Key Best Practices

## Preventing API Key Blocks

### 1. **When Creating Keys**
- Set a credit limit ($5-10) instead of unlimited
- Use descriptive names (e.g., "sting-dev", "sting-prod")
- Create separate keys for dev and production

### 2. **Rate Limiting**
Add rate limiting to your router service to prevent too many requests:

```python
# In agents/router/main.py
from fastapi import HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import time

# Simple rate limiter
request_counts = defaultdict(list)
RATE_LIMIT = 10  # requests
RATE_WINDOW = 60  # seconds

def check_rate_limit(ip: str):
    now = time.time()
    # Clean old requests
    request_counts[ip] = [t for t in request_counts[ip] if now - t < RATE_WINDOW]
    
    if len(request_counts[ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    request_counts[ip].append(now)
```

### 3. **Caching Responses**
Cache common queries to reduce API calls:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_route(question_hash: str):
    # Your routing logic here
    pass

# In your route endpoint
question_hash = hashlib.md5(request.question.encode()).hexdigest()
```

### 4. **Environment-Specific Keys**
Use different keys for different environments:

```bash
# .env.local
OPENROUTER_API_KEY=sk-or-v1-dev-key-here

# .env.production  
OPENROUTER_API_KEY=sk-or-v1-prod-key-here
```

### 5. **Monitoring Usage**
Add logging to track usage:

```python
logger.info(f"API call made - Cost: ${cost}, Total today: ${daily_total}")
```

### 6. **Fallback Keys**
Have backup keys ready:

```python
API_KEYS = [
    os.getenv("OPENROUTER_API_KEY_1"),
    os.getenv("OPENROUTER_API_KEY_2"),
]

# Rotate through keys if one fails
```

### 7. **Request Optimization**
- Use lower token limits where possible
- Use cheaper models for simple routing decisions
- Batch requests when possible

## Emergency Response

If a key gets blocked:

1. Create a new key with a credit limit
2. Update .env files (local and server)
3. Restart services
4. Consider implementing the rate limiting above

## Testing New Keys

Always test a new key locally first:

```bash
curl -X POST https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_NEW_KEY" \
  -H "Content-Type: application/json"
```

This should return a list of available models if the key is valid.