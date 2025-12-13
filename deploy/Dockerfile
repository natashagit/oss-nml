FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY src/ ./src/

RUN uv sync --frozen


RUN uv pip install --python .venv/bin/python -e src/ai_ticket_service

# Runtime-only google deps
RUN uv pip install --python .venv/bin/python \
    google-api-python-client google-auth google-auth-oauthlib

CMD ["uv", "run", "uvicorn", "ai_ticket_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
