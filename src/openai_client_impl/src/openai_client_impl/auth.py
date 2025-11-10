"""OAuth 2.0 authentication module using Google as the identity provider.

This module handles the OAuth flow for authenticating users via Google,
then associates their OpenAI API keys with their Google identity.
"""

import logging
import os
from typing import Any, ClassVar

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow  # type: ignore[import-untyped]

from openai_client_impl.database import CredentialStore

logger = logging.getLogger(__name__)


class OAuthManager:
    """Manages OAuth 2.0 authentication flow using Google.

    This class handles the complete OAuth flow:
    1. Redirecting users to Google for authentication
    2. Handling the callback from Google
    3. Storing user credentials in the database

    Environment Variables:
        GOOGLE_CLIENT_ID: OAuth2 client ID from Google Cloud Console.
        GOOGLE_CLIENT_SECRET: OAuth2 client secret from Google Cloud Console.
        OAUTH_REDIRECT_URI: The redirect URI configured in Google Cloud Console.

    Attributes:
        SCOPES: OAuth scopes required for user authentication.

    """

    SCOPES: ClassVar[list[str]] = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    def __init__(
        self,
        credential_store: CredentialStore | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
    ) -> None:
        """Initialize the OAuth manager.

        Args:
            credential_store: Optional CredentialStore instance for database operations.
                            If None, tokens will not be stored in database (use sessions instead).
            client_id: Google OAuth client ID (or from GOOGLE_CLIENT_ID env var).
            client_secret: Google OAuth client secret (or from GOOGLE_CLIENT_SECRET env var).
            redirect_uri: OAuth redirect URI (or from OAUTH_REDIRECT_URI env var).

        """
        self.credential_store = credential_store
        self.client_id = client_id or os.environ.get("GOOGLE_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.environ.get(
            "OAUTH_REDIRECT_URI", "http://127.0.0.1:8000/oauth/callback",
        )

        if not self.client_id or not self.client_secret:
            msg = (
                "Google OAuth credentials not configured. "
                "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
            )
            raise ValueError(msg)

    def get_authorization_url(self, state: str | None = None) -> tuple[str, str]:
        """Generate the Google OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection.

        Returns:
            A tuple of (authorization_url, state).
            The state should be stored in the session to verify the callback.

        """
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                },
            },
            scopes=self.SCOPES,
            state=state,
        )
        flow.redirect_uri = self.redirect_uri

        authorization_url, state = flow.authorization_url(
            access_type="offline",  # Request refresh token
            include_granted_scopes="true",
            prompt="consent",  # Force consent screen to get refresh token
        )

        return authorization_url, state  # type: ignore[return-value]

    def handle_callback(
        self, authorization_response: str, state: str | None = None,
    ) -> dict[str, Any]:
        """Handle the OAuth callback from Google.

        Args:
            authorization_response: The full callback URL from Google.
            state: The state parameter from the original authorization request.

        Returns:
            A dictionary containing user information:
                - user_id: Unique Google user ID
                - email: User's email address
                - name: User's display name

        Raises:
            ValueError: If the callback processing fails.

        """
        try:
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri],
                    },
                },
                scopes=self.SCOPES,
                state=state,
            )
            flow.redirect_uri = self.redirect_uri

            # Exchange authorization code for tokens
            flow.fetch_token(authorization_response=authorization_response)

            credentials: Credentials = flow.credentials  # type: ignore[assignment]

            # Get user info
            user_info = self._get_user_info(credentials)

            # Store Google refresh token in database only if credential_store is provided
            if self.credential_store is not None:
                self.credential_store.store_user_credentials(
                    user_id=user_info["user_id"],
                    email=user_info["email"],
                    google_refresh_token=credentials.refresh_token,
                )

        except Exception as e:
            logger.exception("Failed to handle OAuth callback")
            msg = f"OAuth callback failed: {e}"
            raise ValueError(msg) from e
        else:
            logger.info("Successfully authenticated user %s", user_info["email"])
            return user_info

    def _get_user_info(self, credentials: Credentials) -> dict[str, str]:
        """Retrieve user information from Google using the access token.

        Args:
            credentials: Google OAuth credentials with a valid access token.

        Returns:
            Dictionary with user_id, email, and name.

        """
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {credentials.token}"},
            timeout=10,
        )
        response.raise_for_status()
        user_data = response.json()

        return {
            "user_id": user_data["id"],
            "email": user_data["email"],
            "name": user_data.get("name", user_data["email"]),
        }

    def refresh_google_token(self, user_id: str) -> Credentials | None:
        """Refresh the Google OAuth token for a user.

        Args:
            user_id: The unique user identifier.

        Returns:
            Refreshed Credentials object or None if refresh fails.

        """
        if self.credential_store is None:
            logger.warning("No credential store available for user %s", user_id)
            return None

        refresh_token = self.credential_store.get_google_refresh_token(user_id)
        if not refresh_token:
            logger.warning("No refresh token found for user %s", user_id)
            return None

        try:
            credentials = Credentials(  # type: ignore[no-untyped-call]
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",  # noqa: S106
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.SCOPES,
            )

            credentials.refresh(Request())  # type: ignore[no-untyped-call]
        except Exception:
            logger.exception("Failed to refresh token for user %s", user_id)
            return None
        else:
            return credentials
