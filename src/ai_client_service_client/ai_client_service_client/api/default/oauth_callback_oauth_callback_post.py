from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.o_auth_callback_request import OAuthCallbackRequest
from ...models.o_auth_callback_response import OAuthCallbackResponse
from ...types import Response


def _get_kwargs(
    *,
    body: OAuthCallbackRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/oauth/callback",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, OAuthCallbackResponse]]:
    if response.status_code == 200:
        response_200 = OAuthCallbackResponse.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, OAuthCallbackResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: OAuthCallbackRequest,
) -> Response[Union[HTTPValidationError, OAuthCallbackResponse]]:
    """Oauth Callback

     Handle OAuth 2.0 callback.

    Args:
        callback_data: OAuth callback data.
        credential_store: Credential store dependency.

    Returns:
        OAuthCallbackResponse: OAuth callback result.

    Args:
        body (OAuthCallbackRequest): Request model for OAuth callback.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, OAuthCallbackResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: OAuthCallbackRequest,
) -> Optional[Union[HTTPValidationError, OAuthCallbackResponse]]:
    """Oauth Callback

     Handle OAuth 2.0 callback.

    Args:
        callback_data: OAuth callback data.
        credential_store: Credential store dependency.

    Returns:
        OAuthCallbackResponse: OAuth callback result.

    Args:
        body (OAuthCallbackRequest): Request model for OAuth callback.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, OAuthCallbackResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: OAuthCallbackRequest,
) -> Response[Union[HTTPValidationError, OAuthCallbackResponse]]:
    """Oauth Callback

     Handle OAuth 2.0 callback.

    Args:
        callback_data: OAuth callback data.
        credential_store: Credential store dependency.

    Returns:
        OAuthCallbackResponse: OAuth callback result.

    Args:
        body (OAuthCallbackRequest): Request model for OAuth callback.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, OAuthCallbackResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: OAuthCallbackRequest,
) -> Optional[Union[HTTPValidationError, OAuthCallbackResponse]]:
    """Oauth Callback

     Handle OAuth 2.0 callback.

    Args:
        callback_data: OAuth callback data.
        credential_store: Credential store dependency.

    Returns:
        OAuthCallbackResponse: OAuth callback result.

    Args:
        body (OAuthCallbackRequest): Request model for OAuth callback.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, OAuthCallbackResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
