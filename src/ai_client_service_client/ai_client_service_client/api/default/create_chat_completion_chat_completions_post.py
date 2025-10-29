from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chat_completion_request import ChatCompletionRequest
from ...models.chat_completion_response import ChatCompletionResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: ChatCompletionRequest,
    user_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["user_id"] = user_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/chat/completions",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ChatCompletionResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = ChatCompletionResponse.from_dict(response.json())

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
) -> Response[Union[ChatCompletionResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ChatCompletionRequest,
    user_id: str,
) -> Response[Union[ChatCompletionResponse, HTTPValidationError]]:
    """Create Chat Completion

     Create a chat completion.

    Args:
        request: Chat completion request data.
        user_id: User ID for authentication.
        client: Injected AI client instance.

    Returns:
        ChatCompletionResponse: Chat completion result.

    Raises:
        HTTPException: If the request fails.

    Args:
        user_id (str):
        body (ChatCompletionRequest): Request model for chat completion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ChatCompletionResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        user_id=user_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ChatCompletionRequest,
    user_id: str,
) -> Optional[Union[ChatCompletionResponse, HTTPValidationError]]:
    """Create Chat Completion

     Create a chat completion.

    Args:
        request: Chat completion request data.
        user_id: User ID for authentication.
        client: Injected AI client instance.

    Returns:
        ChatCompletionResponse: Chat completion result.

    Raises:
        HTTPException: If the request fails.

    Args:
        user_id (str):
        body (ChatCompletionRequest): Request model for chat completion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ChatCompletionResponse, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
        user_id=user_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ChatCompletionRequest,
    user_id: str,
) -> Response[Union[ChatCompletionResponse, HTTPValidationError]]:
    """Create Chat Completion

     Create a chat completion.

    Args:
        request: Chat completion request data.
        user_id: User ID for authentication.
        client: Injected AI client instance.

    Returns:
        ChatCompletionResponse: Chat completion result.

    Raises:
        HTTPException: If the request fails.

    Args:
        user_id (str):
        body (ChatCompletionRequest): Request model for chat completion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ChatCompletionResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        user_id=user_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ChatCompletionRequest,
    user_id: str,
) -> Optional[Union[ChatCompletionResponse, HTTPValidationError]]:
    """Create Chat Completion

     Create a chat completion.

    Args:
        request: Chat completion request data.
        user_id: User ID for authentication.
        client: Injected AI client instance.

    Returns:
        ChatCompletionResponse: Chat completion result.

    Raises:
        HTTPException: If the request fails.

    Args:
        user_id (str):
        body (ChatCompletionRequest): Request model for chat completion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ChatCompletionResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            user_id=user_id,
        )
    ).parsed
