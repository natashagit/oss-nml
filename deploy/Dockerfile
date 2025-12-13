FROM python:3.11-slim

WORKDIR /app

# system deps for git installs
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# install uv
RUN pip install --no-cache-dir uv

# copy only metadata first (cache-friendly)
COPY pyproject.toml uv.lock ./

# install all deps including git + workspace
RUN uv sync --frozen

# now copy source
COPY src/ ./src/

# no PYTHONPATH needed
CMD ["uv", "run", "uvicorn", "ai_ticket_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
