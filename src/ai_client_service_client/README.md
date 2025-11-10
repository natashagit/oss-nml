# ai-client-service-client

Auto-generated Python client library for the AI Client Service API.

## Overview

This package is automatically generated from the OpenAPI specification of the AI Client Service using `openapi-python-client`. It provides strongly-typed methods for interacting with all service endpoints.

**Note**: This package is auto-generated. Do not edit it manually. To regenerate:

```bash
# Start the AI service
uv run uvicorn ai_client_service.main:app --host 127.0.0.1 --port 8000

# Generate the client
uv run openapi-python-client generate \
    --url http://127.0.0.1:8000/openapi.json \
    --output src/ai_client_service_client
```

## Usage

First, create a client:

```python
from ai_client_service_client import Client

client = Client(base_url="http://127.0.0.1:8000")
```

If the endpoints you're going to hit require authentication, use `AuthenticatedClient` instead:

```python
from ai_client_service_client import AuthenticatedClient

client = AuthenticatedClient(base_url="http://127.0.0.1:8000", token="SuperSecretToken")
```

Now call your endpoint and use your models:

```python
from ai_client_service_client.models import ChatCompletionRequest, ChatMessage
from ai_client_service_client.api.default import create_chat_completion_chat_completions_post
from ai_client_service_client.types import Response

with client as client:
    # Create request
    request = ChatCompletionRequest(
        messages=[ChatMessage(role="user", content="Hello!")],
        model="gpt-3.5-turbo"
    )
    
    # Make request
    response: Response[ChatCompletionResponse] = create_chat_completion_chat_completions_post.sync_detailed(
        client=client,
        body=request
    )
    
    if response.parsed:
        print(response.parsed.message.content)
```

Or do the same thing with an async version:

```python
from ai_client_service_client.models import ChatCompletionRequest, ChatMessage
from ai_client_service_client.api.default import create_chat_completion_chat_completions_post

async with client as client:
    request = ChatCompletionRequest(
        messages=[ChatMessage(role="user", content="Hello!")],
        model="gpt-3.5-turbo"
    )
    
    response = await create_chat_completion_chat_completions_post.asyncio(
        client=client,
        body=request
    )
    
    if response:
        print(response.message.content)
```

## SSL Verification

By default, when you're calling an HTTPS API it will attempt to verify that SSL is working correctly. Using certificate verification is highly recommended most of the time, but sometimes you may need to authenticate to a server (especially an internal server) using a custom certificate bundle.

```python
client = AuthenticatedClient(
    base_url="https://internal_api.example.com", 
    token="SuperSecretToken",
    verify_ssl="/path/to/certificate_bundle.pem",
)
```

You can also disable certificate validation altogether, but beware that **this is a security risk**.

```python
client = AuthenticatedClient(
    base_url="https://internal_api.example.com", 
    token="SuperSecretToken", 
    verify_ssl=False
)
```

## Key Features

1. Every path/method combo becomes a Python module with four functions:
   - `sync`: Blocking request that returns parsed data (if successful) or `None`
   - `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful
   - `asyncio`: Like `sync` but async instead of blocking
   - `asyncio_detailed`: Like `sync_detailed` but async instead of blocking

2. All path/query params, and bodies become method arguments.

3. If your endpoint had any tags on it, the first tag will be used as a module name for the function.

4. Any endpoint which did not have a tag will be in `ai_client_service_client.api.default`

## Advanced Customizations

There are more settings on the generated `Client` class which let you control more runtime behavior, check out the docstring on that class for more info. You can also customize the underlying `httpx.Client` or `httpx.AsyncClient`:

```python
from ai_client_service_client import Client

def log_request(request):
    print(f"Request event hook: {request.method} {request.url} - Waiting for response")

def log_response(response):
    request = response.request
    print(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")

client = Client(
    base_url="http://127.0.0.1:8000",
    httpx_args={"event_hooks": {"request": [log_request], "response": [log_response]}},
)
```

## Building / Publishing

This project uses [uv](https://github.com/astral-sh/uv) to manage dependencies and packaging:

1. Update the metadata in `pyproject.toml` (e.g. authors, version).
2. If you're using a private repository: https://docs.astral.sh/uv/guides/integration/alternative-indexes/
3. Build a distribution with `uv build`, builds `sdist` and `wheel` by default.
4. Publish the client with `uv publish`, see documentation for publishing to private indexes.

If you want to install this client into another project without publishing it (e.g. for development):

1. If that project **is using uv**, you can simply do `uv add <path-to-this-client>` from that project
2. If that project is not using uv:
   - Build a wheel with `uv build --wheel`
   - Install that wheel from the other project `pip install <path-to-wheel>`

## Note for Developers

This client is typically used by the `ai_client_adapter` package, which provides a higher-level interface. Most users should use the adapter rather than this client directly.
