FROM ghcr.io/astral-sh/uv:python3.11-bookworm
WORKDIR /app
USER root

COPY pyproject.toml uv.lock* ./
COPY src ./src

ENV UV_SYSTEM_PYTHON=1
RUN uv sync --frozen --no-dev
RUN uv pip install "fastapi" "uvicorn[standard]"

# install each package (editable or regular)
RUN uv pip install -e /app/src/mail_client_api \
                   -e /app/src/gmail_client_impl \
                   -e /app/src/mail_client_service \
                   -e /app/src/mail_client_adapter

# drop privileges
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000

# no --app-dir needed once installed!
CMD ["uv", "run", "uvicorn", "mail_client_service.main:app","--host", "0.0.0.0", "--port", "8000"]
