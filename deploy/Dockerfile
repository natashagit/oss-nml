FROM python:3.11-slim

WORKDIR /app

# FIX 1: Pin OpenAI to 2.9.0 to match your uv.lock
# FIX 2: Install python-multipart (often needed) and other deps
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    prometheus-fastapi-instrumentator \
    openai==2.9.0 \
    httpx \
    python-dotenv \
    python-multipart

# Copy the source code
COPY src/ ./src/

# FIX 3: COMPLEX PYTHONPATH
# CRITICAL FIX: Add /app/src/tickets_api to the path.
ENV PYTHONPATH="/app/src/ai_service/src:/app/src/ai_api/src:/app/src/openai_impl/src:/app/src/ai_ticket_service/src:/app/src/tickets_api/src:/app/src/tickets_client_impl/src"


# CRITICAL CHANGE: Launch the integrated service
CMD ["uvicorn", "ai_ticket_service.main:app", "--host", "0.0.0.0", "--port", "8000"]