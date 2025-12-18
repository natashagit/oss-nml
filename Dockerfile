FROM ghcr.io/astral-sh/uv:python3.11-bookworm
WORKDIR /app
USER root

COPY pyproject.toml uv.lock* ./
COPY src ./src

ENV UV_SYSTEM_PYTHON=1
RUN uv sync --frozen --extra dev --all-packages

# drop privileges
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000

# Run the AI ticket service
CMD [".venv/bin/python", "-m", "uvicorn", "ai_ticket_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
