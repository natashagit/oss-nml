FROM ghcr.io/astral-sh/uv:python3.11-bookworm
WORKDIR /app
USER root

COPY pyproject.toml uv.lock* ./
COPY src ./src

ENV UV_SYSTEM_PYTHON=1
RUN uv sync --frozen --extra dev
RUN uv pip install "fastapi" "uvicorn[standard]"

# install AI ticket service and its dependencies
RUN uv pip install -e /app/src/ai_api \
                   -e /app/src/openai_impl \
                   -e /app/src/tickets_api \
                   -e /app/src/tickets_client_impl \
                   -e /app/src/ai_ticket_service \
                   -e /app/src/ai_ticket_adapter

# drop privileges
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000

# Run the AI ticket service
CMD ["uv", "run", "--extra", "dev", "uvicorn", "ai_ticket_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
