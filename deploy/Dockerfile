FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY src/ ./src/

RUN uv sync --frozen --extra dev

# Install AI ticket service and all its dependencies
RUN uv pip install --python .venv/bin/python \
    -e src/ai_api \
    -e src/openai_impl \
    -e src/tickets_api \
    -e src/tickets_client_impl \
    -e src/ai_ticket_service \
    -e src/ai_ticket_adapter

# Runtime-only google deps
RUN uv pip install --python .venv/bin/python \
    google-api-python-client google-auth google-auth-oauthlib

CMD ["uv", "run", "--extra", "dev", "uvicorn", "ai_ticket_service.main:app", "--host", "0.0.0.0", "--port", "8000"]