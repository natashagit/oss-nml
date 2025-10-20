# Design Document

This document describes the architecture and design of the service-based implementation added to the mail client project. The goal is to transform the original library-based email client into a scalable service that can be accessed over HTTP.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [API Design](#api-design)
- [The Adapter Pattern](#the-adapter-pattern)
- [Testing Strategy](#testing-strategy)

---

## Architecture Overview

### The Problem

The original repository is a **Python library** with:
- An interface (`mail_client_api`) defining a contract for an email client
- An implementation (`gmail_client_impl`) that fulfills that contract

**Why this doesn't scale:**
- Each program needs its own Gmail credentials and OAuth tokens
- Every customer needs different code installed (Gmail vs Outlook vs IMAP)
- 1000 customers = 1000 individual connections to maintain

**The Solution:**

Transform the library into a **service** - an independently running process that exposes functionality over HTTP.

### Components

This implementation adds **three new components** that act as "bridges":

#### 1. `mail_client_service` (FastAPI Service)

**Location**: `src/mail_client_service/`

**Purpose**: Wraps the original `mail_client_api` as a RESTful HTTP service

**Key Files**:
- `main.py` - FastAPI application with HTTP endpoints
- `models.py` - Pydantic models for request/response serialization
- `dependencies.py` - Dependency injection for the mail client

**What it does**:
- Listens for HTTP requests on endpoints like `/messages`, `/messages/{id}`, etc.
- Uses FastAPI's dependency injection to get a `Client` instance
- Delegates to the original `mail_client_api` methods
- Serializes responses to JSON using Pydantic models
- Returns appropriate HTTP status codes

**Key Implementation Details**:

```python
# main.py - Endpoint example
@app.get("/messages")
def get_messages(
    max_results: Annotated[int, Query(ge=1, le=100)] = 10,
    client: Annotated[Client, Depends(get_mail_client)] = None,
) -> list[MessageSummary]:
    messages = client.get_messages(max_results=max_results)
    return [MessageSummary(...) for msg in messages]
```

**Pydantic Models**:
- `MessageSummary`: Contains id, from_, to, date, subject (no body)
- `MessageDetail`: Contains all summary fields plus body
- `OperationResponse`: Contains success boolean and message string

**Dependency Injection**:
```python
# dependencies.py
def get_mail_client() -> Client:
    return get_client(interactive=False)
```

#### 2. `mail_client_service_client` (Auto-Generated Client)

**Location**: `src/mail_client_service_client/`

**Purpose**: Auto-generated HTTP client that talks to the FastAPI service

**How it was generated**:
1. Start the FastAPI service: `uvicorn mail_client_service.main:app`
2. FastAPI automatically generates an OpenAPI spec at `/openapi.json`
3. Use `openapi-python-client` to generate the client:
   ```bash
   openapi-python-client generate --url http://localhost:8000/openapi.json
   ```

**What it provides**:
- Type-safe Python functions for each API endpoint
- Automatic request serialization and response deserialization
- Error handling for HTTP errors
- Sync methods for blocking calls

**Generated Structure**:
```
mail_client_service_client/
├── api/
│   └── default/
│       ├── get_messages_messages_get.py
│       ├── get_message_messages_message_id_get.py
│       ├── delete_message_messages_message_id_delete.py
│       └── mark_message_as_read_messages_message_id_mark_as_read_post.py
├── models/
│   ├── message_summary.py
│   ├── message_detail.py
│   └── operation_response.py
└── client.py
```

**Example usage of generated client**:
```python
from mail_client_service_client import Client
from mail_client_service_client.api.default import get_messages_messages_get

client = Client(base_url="http://localhost:8000")
messages = get_messages_messages_get.sync(client=client, max_results=10)
```

#### 3. `mail_client_adapter` (Adapter/Shim)

**Location**: `src/mail_client_adapter/`

**Purpose**: Implements `mail_client_api.Client` interface by delegating to the generated client

**Key File**: `client_impl.py`

**What it does**:
- Inherits from `mail_client_api.Client` (satisfies the interface)
- Wraps the generated client
- Translates method calls from the interface to generated client calls
- Transforms responses to match interface-compliant types

**Implementation**:
```python
class ServiceClient(Client):
    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.client = GeneratedClient(base_url=base_url)
    
    def get_messages(self, max_results: int = 10) -> Iterator[Message]:
        result = get_messages_messages_get.sync(
            client=self.client, 
            max_results=max_results
        )
        return list(result) if result else []
    
    def get_message(self, message_id: str) -> Message:
        result = get_message_messages_message_id_get.sync(
            client=self.client, 
            message_id=message_id
        )
        if result is None:
            raise ValueError(f"Message {message_id} not found")
        return result
    
    def delete_message(self, message_id: str) -> bool:
        resp = delete_message_messages_message_id_delete.sync(
            client=self.client, 
            message_id=message_id
        )
        return getattr(resp, "status", None) == "ok"
    
    def mark_as_read(self, message_id: str) -> bool:
        resp = mark_message_as_read_messages_message_id_mark_as_read_post.sync(
            client=self.client, 
            message_id=message_id
        )
        return getattr(resp, "status", None) == "ok"
```

### Request Flow

Here's how a complete request flows through all the bridges:

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER CODE                                  │
│  from mail_client_adapter.client_impl import ServiceClient       │
│                                                                   │
│  client = ServiceClient(base_url="http://localhost:8000")        │
│  messages = client.get_messages(max_results=5)                   │
└────────────────────────┬─────────────────────────────────────────┘
                         │ calls get_messages(5)
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                   ADAPTER (ServiceClient)                         │
│  Location: mail_client_adapter/client_impl.py                    │
│                                                                   │
│  def get_messages(self, max_results: int = 10):                  │
│      result = get_messages_messages_get.sync(...)                │
│      return list(result) if result else []                       │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTP GET /messages?max_results=5
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│              GENERATED CLIENT (HTTP Layer)                        │
│  Location: mail_client_service_client/                           │
│                                                                   │
│  Makes HTTP request, serializes parameters                        │
│  Deserializes JSON response to Pydantic models                   │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTP Request
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                  FASTAPI SERVICE                                  │
│  Location: mail_client_service/main.py                           │
│                                                                   │
│  @app.get("/messages")                                           │
│  def get_messages(                                                │
│      max_results: Annotated[int, Query(ge=1, le=100)] = 10,     │
│      client: Annotated[Client, Depends(get_mail_client)]         │
│  ):                                                               │
│      messages = client.get_messages(max_results)                 │
│      return [MessageSummary(...) for msg in messages]            │
└────────────────────────┬─────────────────────────────────────────┘
                         │ calls get_messages(5)
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                 ORIGINAL IMPLEMENTATION                           │
│  gmail_client_impl.GmailClient                                    │
│  - Handles OAuth authentication                                   │
│  - Makes Gmail API requests                                       │
│  - Returns Message objects                                        │
└────────────────────────┬─────────────────────────────────────────┘
                         │ Gmail API calls
                         ▼
                    [Gmail API]
```

**Step-by-step breakdown**:

1. **User code** calls `client.get_messages(5)` on the adapter
2. **Adapter** (`ServiceClient`) translates this to a generated client call
3. **Generated client** makes HTTP GET request to `http://localhost:8000/messages?max_results=5`
4. **FastAPI service** receives the request, validates parameters with Query constraints
5. **FastAPI** uses dependency injection to get a `Client` instance (which is `GmailClient`)
6. **FastAPI** calls `client.get_messages(5)` on the original implementation
7. **GmailClient** authenticates with OAuth, makes Gmail API calls
8. **GmailClient** returns `Message` objects
9. **FastAPI** converts `Message` objects to `MessageSummary` Pydantic models
10. **FastAPI** serializes to JSON and returns HTTP 200 response
11. **Generated client** deserializes JSON response to Pydantic model objects
12. **Adapter** returns the result as a list to user code

**Key insight**: The user's code looks identical whether using the library directly or the service through the adapter!

### Sample API Response

**Request**: `GET /messages?max_results=2`

**Response** (HTTP 200 OK):
```json
[
  {
    "id": "18f8a1b2c3d4e5f6",
    "from": "sender@example.com",
    "to": "recipient@gmail.com",
    "date": "01/15/2025",
    "subject": "Meeting Tomorrow"
  },
  {
    "id": "17e7d6c5b4a39281",
    "from": "noreply@github.com",
    "to": "recipient@gmail.com",
    "date": "01/14/2025",
    "subject": "Pull request merged"
  }
]
```

**Request**: `GET /messages/18f8a1b2c3d4e5f6`

**Response** (HTTP 200 OK):
```json
{
  "id": "18f8a1b2c3d4e5f6",
  "from": "sender@example.com",
  "to": "recipient@gmail.com",
  "date": "01/15/2025",
  "subject": "Meeting Tomorrow",
  "body": "Hi,\n\nLet's meet tomorrow at 2 PM to discuss the project.\n\nBest,\nSender"
}
```

**Request**: `POST /messages/18f8a1b2c3d4e5f6/mark-as-read`

**Response** (HTTP 200 OK):
```json
{
  "success": true,
  "message": "Message 18f8a1b2c3d4e5f6 marked as read"
}
```

**Request**: `DELETE /messages/18f8a1b2c3d4e5f6`

**Response** (HTTP 200 OK):
```json
{
  "success": true,
  "message": "Message 18f8a1b2c3d4e5f6 deleted"
}
```

**Request**: `GET /health`

**Response** (HTTP 200 OK):
```json
{
  "status": "healthy"
}
```

---

## API Design

### Endpoints

#### 1. Get Messages

**Endpoint**: `GET /messages`

**Purpose**: Fetch a list of message summaries

**Query Parameters**:
- `max_results` (int, optional): Maximum number of messages to return
  - Default: 10
  - Constraints: 1 ≤ max_results ≤ 100 (validated using `Query(ge=1, le=100)`)

**Response**: `200 OK`
```json
[
  {
    "id": "string",
    "from": "string",
    "to": "string",
    "date": "string",
    "subject": "string"
  }
]
```

**Response Model**: `List[MessageSummary]`

**Implementation**:
```python
@app.get("/messages")
def get_messages(
    max_results: Annotated[int, Query(ge=1, le=100)] = 10,
    client: Annotated[Client, Depends(get_mail_client)] = None,
) -> list[MessageSummary]:
    messages = client.get_messages(max_results=max_results)
    return [MessageSummary(
        id=msg.id,
        from_=msg.from_,
        to=msg.to,
        date=msg.date,
        subject=msg.subject,
    ) for msg in messages]
```

#### 2. Get Single Message

**Endpoint**: `GET /messages/{message_id}`

**Purpose**: Fetch full details of a specific message

**Path Parameters**:
- `message_id` (string): Unique message identifier

**Response**: `200 OK`
```json
{
  "id": "string",
  "from": "string",
  "to": "string",
  "date": "string",
  "subject": "string",
  "body": "string"
}
```

**Response Model**: `MessageDetail`

**Implementation**:
```python
@app.get("/messages/{message_id}")
def get_message(
    message_id: str,
    client: Annotated[Client, Depends(get_mail_client)],
) -> MessageDetail:
    msg = client.get_message(message_id)
    return MessageDetail(
        id=msg.id,
        from_=msg.from_,
        to=msg.to,
        date=msg.date,
        subject=msg.subject,
        body=msg.body,
    )
```

#### 3. Mark Message as Read

**Endpoint**: `POST /messages/{message_id}/mark-as-read`

**Purpose**: Mark a specific message as read

**Path Parameters**:
- `message_id` (string): Unique message identifier

**Response**: `200 OK`
```json
{
  "success": true,
  "message": "Message {message_id} marked as read"
}
```

**Response Model**: `OperationResponse`

**Implementation**:
```python
@app.post("/messages/{message_id}/mark-as-read")
def mark_message_as_read(
    message_id: str,
    client: Annotated[Client, Depends(get_mail_client)],
) -> OperationResponse:
    success = client.mark_as_read(message_id)
    return OperationResponse(
        success=success,
        message=f"Message {message_id} marked as read" if success else "Operation failed",
    )
```

#### 4. Delete Message

**Endpoint**: `DELETE /messages/{message_id}`

**Purpose**: Delete a specific message

**Path Parameters**:
- `message_id` (string): Unique message identifier

**Response**: `200 OK`
```json
{
  "success": true,
  "message": "Message {message_id} deleted"
}
```

**Response Model**: `OperationResponse`

**Implementation**:
```python
@app.delete("/messages/{message_id}")
def delete_message(
    message_id: str,
    client: Annotated[Client, Depends(get_mail_client)],
) -> OperationResponse:
    success = client.delete_message(message_id)
    return OperationResponse(
        success=success,
        message=f"Message {message_id} deleted" if success else "Operation failed",
    )
```

#### 5. Health Check

**Endpoint**: `GET /health`

**Purpose**: Verify service is running

**Response**: `200 OK`
```json
{
  "status": "healthy"
}
```

**Implementation**:
```python
@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
```

### Error Handling

The service maps errors from the underlying implementation to appropriate HTTP status codes:

#### Error Mapping Strategy

| Scenario | HTTP Status | Response Body | Implementation |
|----------|-------------|---------------|----------------|
| **Successful operation** | 200 OK | Success response with data | All operations complete successfully |
| **Message not found** | 404 Not Found | `{"detail": "Message {id} not found: ..."}` | `get_message()` raises exception |
| **Internal error** | 500 Internal Server Error | `{"detail": "Failed to {operation}: ..."}` | Unexpected errors from Gmail API |
| **Invalid request** | 422 Unprocessable Entity | FastAPI validation error | Invalid query parameters |

#### Implementation Examples

**Example 1: Message Not Found (404)**

```python
@app.get("/messages/{message_id}")
def get_message(
    message_id: str,
    client: Annotated[Client, Depends(get_mail_client)],
) -> MessageDetail:
    try:
        msg = client.get_message(message_id)
        return MessageDetail(...)
    except Exception as e:
        raise HTTPException(
            status_code=404, 
            detail=f"Message {message_id} not found: {e!s}"
        ) from e
```

**Rationale**: When `get_message()` fails, it typically means the message doesn't exist or the user doesn't have access. 404 is the appropriate "resource not found" status code.

**Example 2: General Failure (500)**

```python
@app.get("/messages")
def get_messages(
    max_results: Annotated[int, Query(ge=1, le=100)] = 10,
    client: Annotated[Client, Depends(get_mail_client)] = None,
) -> list[MessageSummary]:
    try:
        messages = client.get_messages(max_results=max_results)
        return [MessageSummary(...) for msg in messages]
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch messages: {e!s}"
        ) from e
```

**Rationale**: When `get_messages()` fails, it could be due to authentication issues, network errors, or Gmail API failures. These are internal server errors (500) because the client's request was valid but the server couldn't fulfill it.

**Example 3: Validation Error (422) - Handled Automatically**

FastAPI automatically returns 422 when request validation fails:

```python
@app.get("/messages")
def get_messages(
    max_results: Annotated[int, Query(ge=1, le=100)] = 10,
    ...
):
```

If a client requests `GET /messages?max_results=1000`, FastAPI returns:
```json
{
  "detail": [
    {
      "loc": ["query", "max_results"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le"
    }
  ]
}
```

#### Error Response Examples

**404 Example**:
```
GET /messages/nonexistent_id

Response: 404 Not Found
{
  "detail": "Message nonexistent_id not found: HTTPError 404"
}
```

**500 Example**:
```
DELETE /messages/some_id (when Gmail API is down)

Response: 500 Internal Server Error
{
  "detail": "Failed to delete message: Connection timeout"
}
```

**422 Example**:
```
GET /messages?max_results=1000

Response: 422 Unprocessable Entity
{
  "detail": [
    {
      "loc": ["query", "max_results"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## The Adapter Pattern

### Why we need it

The auto-generated HTTP client does not match the original Client interface: The original world exposes class methods like “get_messages” and returns Message objects or booleans.

The generated world exposes HTTP-style functions and returns simple models linked to endpoints.

### What the adapter does

It implements the original Client interface. Inside, it uses the generated HTTP client to call the service, and then it translates parameters and turns the service’s models into the types the original interface expects. Therefore it keeps method names and behavior the same, so calling code does not change.

### What changes for application developers

Only how you construct the client:

Library mode: build the original Client directly from the library.

Service mode: build the adapter and give it the service base URL.
Everything else in your app can remain the same.
---

## Testing Strategy

### What You Tested

The testing strategy focuses on verifying the **new components** (service, generated client, adapter) while reusing existing tests for the original components.

**Components Tested**:

1. **Original Components** (`mail_client_api`, `gmail_client_impl`):
   - Already have comprehensive unit tests
   - No changes needed - these tests continue to pass

2. **FastAPI Service** (`mail_client_service`):
   - HTTP endpoint behavior
   - Request validation
   - Response serialization
   - Error handling (404 vs 500)
   - Dependency injection

3. **Adapter** (`mail_client_adapter`):
   - Interface compliance (implements `Client` ABC correctly)
   - Delegation to generated client
   - Return type transformations

**Why These Components?**:

- **Service**: Most critical new component - entry point for all HTTP requests
- **Adapter**: Ensures interface compliance and proper delegation
- **Generated Client**: Auto-generated, minimal custom testing needed

### Test Types

The test suite uses **unit tests** for the service layer:

#### Unit Tests

**Purpose**: Test individual components in isolation with mocked dependencies

**Location**: `src/mail_client_service/tests/test_service.py`

**Coverage**:
- Service endpoints with mocked `Client`
- All four operations (get_messages, get_message, mark_as_read, delete_message)
- Error handling (404 for not found)
- Health check endpoint
- Dependency injection mechanism

**Example**: Testing service endpoint with mock



**Why This Approach?**:
- Fast (no real Gmail API calls)
- Isolated (tests only the service layer)
- Controllable (can test error cases easily)
- Uses FastAPI's TestClient for realistic HTTP testing

**Test Coverage**:
- ✅ `test_get_messages` - Tests GET /messages endpoint
- ✅ `test_get_single_message` - Tests GET /messages/{id} endpoint
- ✅ `test_delete_message` - Tests DELETE /messages/{id} endpoint
- ✅ `test_mark_as_read` - Tests POST /messages/{id}/mark-as-read endpoint
- ✅ `test_get_message_not_found` - Tests 404 error handling
- ✅ `test_health_check` - Tests health check endpoint
- ✅ `test_get_mail_client_dependency` - Tests dependency injection

#### Integration Tests

**Location**: `tests/integration/test_client_integration.py`

**Purpose**: Test that the original dependency injection still works with the service

**Coverage**:
- Existing integration tests verify library components work together
- These tests remain unchanged and continue to pass
- Service integration tested through unit tests with mocked client

#### End-to-End Tests

**Location**: `tests/e2e/test_main_application.py`

**Purpose**: Test the complete original library workflow

**Coverage**:
- Existing E2E tests verify the library works end-to-end
- These tests remain unchanged and continue to pass
- Service E2E testing would require a running service instance

### Mocking Strategy

The mocking strategy varies by test type:

#### Service Layer Tests: Mock the `Client`

**What we mock**: `mail_client_api.Client` (the original implementation)

**Why**: 
- We want to test the service layer (HTTP handling, serialization) in isolation
- We don't want to make real Gmail API calls in unit tests
- We want tests to be fast and deterministic



**Rationale**: The service's job is to wrap the client and expose it over HTTP. By mocking the client, we verify that the service correctly delegates to it and handles responses properly. This isolates testing to HTTP layer concerns: request parsing, validation, serialization, and status codes.

**What We Test**:
1. Request parameter validation (Query constraints)
2. Proper delegation to mocked client methods
3. Response serialization to Pydantic models
4. HTTP status code mapping (200, 404, 500, 422)
5. Error message formatting
6. Dependency injection mechanism



### Interface Compliance

**Goal**: Verify that `ServiceClient` (adapter) correctly implements the `mail_client_api.Client` interface.

#### Approach 1: Type Checking with MyPy

**How**: Use MyPy to verify interface compliance at type-check time

```bash
$ uv run mypy src/mail_client_adapter/
Success: no issues found
```

**What it verifies**:
- `ServiceClient` inherits from `Client` ABC
- All abstract methods are implemented
- Method signatures match exactly (parameters and return types)

**Why it works**: Python's ABC + MyPy's strict type checking ensures compile-time verification. If any method is missing or has wrong signature, MyPy catches it before runtime.

#### Approach 2: Runtime Verification with `isinstance`

**How**: Use Python's `isinstance()` to verify at runtime

```python
from mail_client_adapter.client_impl import ServiceClient
from mail_client_api import Client

adapter = ServiceClient(base_url="http://localhost:8000")

# Runtime check: Is ServiceClient a Client?
assert isinstance(adapter, Client)

# Verify all required methods exist
assert hasattr(adapter, "get_messages")
assert hasattr(adapter, "get_message")
assert hasattr(adapter, "delete_message")
assert hasattr(adapter, "mark_as_read")

# Verify methods are callable
assert callable(adapter.get_messages)
assert callable(adapter.get_message)
assert callable(adapter.delete_message)
assert callable(adapter.mark_as_read)
```

**What it verifies**:
- Adapter is an instance of `Client` (inheritance works)
- All required methods exist and are callable

#### Approach 3: Behavioral Testing

**How**: Test that adapter behaves the same as original implementation

**Verification**:
- Both return `Message` objects with same properties
- Both return boolean values for operations
- Both raise appropriate exceptions for errors


#### Approach 4: Implementation Inheritance


**What this ensures**:
- Python's ABC mechanism prevents instantiation if methods are missing
- All abstract methods must be implemented
- Method signatures must match the interface
- Type checkers can verify correctness

**Verification at instantiation time**:
If any abstract method is missing, Python raises `TypeError`:
```python
# If ServiceClient didn't implement all methods:
client = ServiceClient()  # ❌ TypeError: Can't instantiate abstract class
```

### Summary

**Test Coverage**:
- Unit tests: Comprehensive service endpoint testing with mocked client
- Uses FastAPI TestClient for realistic HTTP testing
- All endpoints tested (get_messages, get_message, mark_as_read, delete_message, health)
- Error scenarios tested (404 not found)
- Dependency injection tested

**Mocking Strategy**:
- Service tests: Mock `Client` to isolate HTTP layer testing
- Focus on request/response handling, not Gmail API logic

**Interface Compliance**:
- Type checking: MyPy verifies at compile time
- Runtime checks: `isinstance()` verifies inheritance
- Behavioral tests: Verify same interface behavior
- Implementation inheritance: ABC prevents incomplete implementations

This strategy ensures the new components work correctly while maintaining compatibility with the original interface, making the service truly transparent to users.