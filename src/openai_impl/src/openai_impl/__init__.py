"""Public exports for the OpenAI implementation package."""

from openai_impl.openai_impl import (
    OpenAIClient,
    get_ai_impl,
    register,
)

__all__ = [
    "OpenAIClient",
    "get_ai_impl",
    "register",
]

# Dependency injection happens at import time
register()
