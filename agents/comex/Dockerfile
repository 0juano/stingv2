FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and prompt
COPY main.py .
COPY prompt.md .

# Environment variables
ENV AGENT_NAME=comex
ENV OPENROUTER_MODEL=openai/gpt-4o-mini

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]