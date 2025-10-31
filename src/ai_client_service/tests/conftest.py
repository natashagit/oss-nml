from fastapi import status  # add this import at the top with others

@app.get("/oauth/authorize")
def oauth_authorize() -> RedirectResponse:
    """Initiate OAuth 2.0 authorization flow."""
    try:
        oauth_manager = OAuthManager()
        auth_url = oauth_manager.get_authorization_url()
        logger.info("Redirecting user to OAuth provider: %s", auth_url)
        # Explicit 307 so tests that assert 307 always pass
        return RedirectResponse(url=auth_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    except Exception as e:
        logger.exception("Failed to initiate OAuth flow")
        raise HTTPException(status_code=500, detail=f"Failed to initiate OAuth flow: {e!s}") from e
