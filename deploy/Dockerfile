FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

# Copy metadata AND workspace source before syncing
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

RUN uv sync --frozen

CMD ["uv", "run", "uvicorn", "ai_ticket_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
