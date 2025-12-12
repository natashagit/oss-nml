"""FastAPI service for AI interface."""

import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException


from prometheus_fastapi_instrumentator import Instrumentator 


import openai_impl  # noqa: F401 - registers default impl
from ai_api import AIInterface, get_client  # type: ignore[attr-defined]
from ai_service.models import GenerateRequest, GenerateResponse, HealthCheckResponse

app = FastAPI(
    title="AI Service",
    description="FastAPI wrapper around AI interface",
    version="0.1.0",
)


# This creates the /metrics endpoint for Prometheus to scrape
Instrumentator().instrument(app).expose(app)
# -----------------------------------------

# Load environment variables from .env if present
load_dotenv()


@app.get("/health")
def health() -> HealthCheckResponse:
    """Health check."""
    return HealthCheckResponse(status="healthy", version=app.version or "0.0.0")


@app.post("/generate")
def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate a response using the registered AI interface."""
    try:
        client: AIInterface = get_client()  # type: ignore[assignment]
    except Exception as exc:  # pragma: no cover - runtime wiring issues
        raise HTTPException(status_code=500, detail=f"Failed to load AI client: {exc!s}") from exc

    try:
        result: str | dict[str, Any] = client.generate_response(
            user_input=request.user_input,
            system_prompt=request.system_prompt,
            response_schema=request.response_schema,
        )
    except Exception as exc:  # pragma: no cover - upstream provider errors
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc!s}") from exc

    return GenerateResponse(result=result)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "ai_service.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )