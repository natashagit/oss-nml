"""OpenAI Client Implementation with OAuth 2.0 authentication.

This implementation supports multiple credential sources:
1. Explicit API key parameter
2. OPENAI_API_KEY environment variable  
3. Database (CredentialStore) for OAuth flow
"""

from openai_client_impl.auth import OAuthManager
from openai_client_impl.database import CredentialStore
from openai_client_impl.openai_impl import OpenAIClient, get_client_impl, register

__all__ = [
    "OpenAIClient",
    "OAuthManager",
    "CredentialStore",
    "get_client_impl",
    "register",
]

# Auto-register the implementation at import time
# This allows using ai_client_api.get_client() without explicit registration
# Credentials are resolved in priority order: parameter -> env var -> database
register()
