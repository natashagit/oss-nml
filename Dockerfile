FROM ghcr.io/astral-sh/uv:python3.11-bookworm
WORKDIR /app
USER root

COPY pyproject.toml uv.lock* ./
COPY src ./src

ENV UV_SYSTEM_PYTHON=1
RUN uv sync --frozen --no-dev

# install workspace packages in editable mode
RUN uv pip install -e /app/src/ai_client_api \
                   -e /app/src/ai_client_adapter \
                   -e /app/src/ai_client_service \
                   -e /app/src/openai_client_impl \
                   -e /app/src/ai_client_service_client \
                   -e /app/src/mail_client_api \
                   -e /app/src/gmail_client_impl \
                   -e /app/src/mail_client_service \
                   -e /app/src/mail_client_adapter \
                   -e /app/src/mail_client_service_client

# drop privileges
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000

# no --app-dir needed once installed!
CMD ["uv", "run", "uvicorn", "ai_client_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
