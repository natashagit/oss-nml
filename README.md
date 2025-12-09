# Python Application Template: Component-Based Architecture

[![CircleCI](https://circleci.com/gh/ivanearisty/oss-taapp.svg?style=shield)](https://circleci.com/gh/ivanearisty/oss-taapp)
[![Coverage](https://img.shields.io/badge/coverage-85%2B%25-brightgreen)](https://circleci.com/gh/ivanearisty/oss-taapp)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

This repository serves as a professional-grade template for modern Python projects. It demonstrates a robust, component-based architecture by building two complete systems:

1. **AI Service Stack**: OpenAI-powered AI assistant with conversational and structured output capabilities
2. **Mail Client Stack**: Gmail API integration for email management

The project emphasizes strict separation of concerns, dependency injection, and a comprehensive automated toolchain to enforce code quality and best practices.

## Architectural Philosophy

This project is built on the principle of "programming integrated over time." The architecture is designed to combat complexity and ensure the system is maintainable and evolvable.

-   **Component-Based Design:** The system is broken down into four distinct, self-contained components. Each component has a single responsibility and can be "forklifted" out of this project to be used in another with minimal effort.
-   **Interface-Implementation Separation:** Every piece of functionality is defined by an abstract **contract** implemented as an ABC (the "what") and fulfilled by a concrete **implementation** (the "how"). This decouples our business logic from specific technologies (like Gmail).
-   **Dependency Injection:** Implementations are "injected" into the abstract contracts at runtime. This means consumers of the API only ever depend on the stable interface, not the volatile implementation details.

## Core Components

The project is a `uv` workspace containing two complete component stacks:

### AI Service Stack

1. **`ai_api`**: Defines the abstract `AIInterface` base class (ABC). This is the contract for AI operations (e.g., `generate_response`).
2. **`openai_impl`**: Provides the `OpenAIClient` class, a concrete implementation using the OpenAI API. Supports both conversational and structured output.
3. **`ai_service`**: A FastAPI service that wraps the `ai_api` interface and exposes REST endpoints (`/generate`, `/health`).
4. **`ai_adapter`**: Wraps an auto-generated client from the OpenAPI spec and implements the `ai_api.AIInterface`. Makes remote service calls feel identical to local library usage.
5. **`ai_service_client`**: Auto-generated Python client package (via `openapi-python-client`) that provides strongly-typed methods for interacting with the AI service.

### Mail Client Stack

1. **`mail_client_api`**: Defines the abstract `Client` base class (ABC). This is the contract for mail client operations (e.g., `get_messages`).
2. **`gmail_client_impl`**: Provides the `GmailClient` class, a concrete implementation using the Gmail API.
3. **`mail_client_service`**: A FastAPI service that wraps the `mail_client_api` interface and exposes REST endpoints (`/messages`, `/messages/{id}`, etc.).
4. **`mail_client_adapter`**: Wraps an auto-generated client and implements the `mail_client_api.Client` interface.
5. **`mail_client_service_client`**: Auto-generated Python client package for interacting with the mail service.

## Project Structure

```
oss-nml/
├── src/                            # Source packages (uv workspace members)
│   ├── ai_api/                     # Abstract AI interface (ABC)
│   ├── openai_impl/                # OpenAI-specific implementation
│   ├── ai_service/                 # FastAPI web service for AI
│   ├── ai_adapter/                 # Adapter wrapping service client
│   ├── ai_service_client/          # Auto-generated AI service client
│   ├── mail_client_api/            # Abstract mail client base class (ABC)
│   ├── gmail_client_impl/          # Gmail-specific client implementation
│   ├── mail_client_service/        # FastAPI web service for mail
│   ├── mail_client_adapter/        # Adapter wrapping mail service client
│   └── mail_client_service_client/ # Auto-generated mail service client
├── tests/                          # Integration and E2E tests
│   ├── integration/                # Component integration tests
│   └── e2e/                        # End-to-end application tests
├── docs/                           # Documentation source files
├── .circleci/                      # CircleCI configuration
├── main.py                         # AI service demo entry point
├── pyproject.toml                  # Project configuration (dependencies, tools)
├── uv.lock                         # Locked dependency versions
└── .env.example                    # Example environment variables
```

## Project Setup

### 1. Prerequisites

-   Python 3.11 or higher
-   `uv` – A fast, all-in-one Python package manager.

### 2. Initial Setup

1.  **Install `uv`:**
    ```bash
    # macOS / Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Windows (PowerShell)
    irm https://astral.sh/uv/install.ps1 | iex
    ```

2.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd ta-assignment
    ```

3.  **Set Up API Credentials:**

    **For AI Service (Required):**
    ```bash
    export OPENAI_API_KEY="your_openai_api_key_here"
    ```
    
    Or create a `.env` file:
    ```env
    OPENAI_API_KEY=your_openai_api_key_here
    ```

    **For Gmail Service (Optional):**
    -   Follow the [Google Cloud instructions](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application) to enable the Gmail API and download your OAuth 2.0 credentials.
    -   Rename the downloaded file to `credentials.json` and place it in the root of this project.
    -   **Alternative**: For CI/CD environments, you can use environment variables instead:
        ```bash
        export GMAIL_CLIENT_ID="your_client_id"
        export GMAIL_CLIENT_SECRET="your_client_secret"
        export GMAIL_REFRESH_TOKEN="your_refresh_token"
        ```
    -   **Important:** Credential files contain secrets and are ignored by `.gitignore`.

4.  **Create and Sync the Virtual Environment:**
    This single command creates a `.venv` folder and installs all packages (including workspace members and development tools) defined in `uv.lock`.
    ```bash
    uv sync --all-packages --extra dev
    ```

5.  **Activate the Virtual Environment:**
    ```bash
    # macOS / Linux
    source .venv/bin/activate
    # Windows (PowerShell)
    .venv\Scripts\Activate.ps1
    ```

6.  **Run the AI Demo:**
    ```bash
    # Terminal 1: Start the AI service
    uv run uvicorn ai_service.main:app --reload
    
    # Terminal 2: Run the demo
    uv run python main.py
    ```
    
    **For Gmail (Optional):**
    Run the mail client once to perform the interactive OAuth flow. This will open a browser window for you to grant permission. After you approve, a `token.json` file will be created.

## How to Run

### Running the AI Service Demo

The main demo (`main.py`) demonstrates the AI service with both conversational and structured output:

```bash
# 1. Set your OpenAI API key
export OPENAI_API_KEY="your_openai_api_key_here"

# 2. Start the AI service (Terminal 1)
uv run uvicorn ai_service.main:app --reload

# 3. Run the demo (Terminal 2)
uv run python main.py
```

**Expected Output:**

```
Conversational response: Hello there friend!
Structured response: {'intent': 'create_ticket', 'title': 'Fix login redirect'}
AI demo complete.
```

### Running with Local Implementation (No Service)

You can also run the AI client directly without the service:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"

python -c "
import openai_impl
from ai_api import get_client

client = get_client()
response = client.generate_response(
    'What is 2+2?',
    'You are a math tutor.'
)
print(response)
"
```

### Sample Input/Output Examples

#### Example 1: Conversational Response (No Schema)

```python
import openai_impl
from ai_api import get_client

client = get_client()

response = client.generate_response(
    user_input="Explain Python decorators in one sentence.",
    system_prompt="You are concise and clear."
)

print(response)
# Output: "Python decorators are functions that modify the behavior of other functions or classes."
```

#### Example 2: Structured Output (With Schema)

```python
import openai_impl
from ai_api import get_client

client = get_client()

# Define a schema for email action extraction
schema = {
    "name": "email_action",
    "description": "Extract email action intent and parameters",
    "schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["delete", "mark_as_read", "get_message", "list_messages"]
            },
            "message_id": {"type": "string"}
        },
        "required": ["action"],
        "additionalProperties": False
    }
}

response = client.generate_response(
    user_input="Delete the email with ID 12345",
    system_prompt="Extract the email action and parameters.",
    response_schema=schema
)

print(response)
# Output: {"action": "delete", "message_id": "12345"}
```

#### Example 3: Intent Detection

```python
import openai_impl
from ai_api import get_client

client = get_client()

schema = {
    "name": "intent_detection",
    "description": "Detect user intent",
    "schema": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "enum": ["email_management", "weather_query", "general_conversation"]
            },
            "confidence": {"type": "number"}
        },
        "required": ["intent", "confidence"],
        "additionalProperties": False
    }
}

response = client.generate_response(
    user_input="Show me my last 5 unread emails",
    system_prompt="Analyze the user's intent.",
    response_schema=schema
)

print(response)
# Output: {"intent": "email_management", "confidence": 0.95}
```

#### Example 4: Using the Remote Service (via Adapter)

```bash
# Terminal 1: Start the service
export OPENAI_API_KEY="your_key"
uv run uvicorn ai_service.main:app --reload

# Terminal 2: Use the adapter
python -c "
import ai_adapter
from ai_api import get_client

# Register the adapter to use the remote service
ai_adapter.register(base_url='http://127.0.0.1:8000')

client = get_client()
response = client.generate_response(
    'Say hello in 3 words',
    'You are concise.'
)
print(response)
"
# Output: "Hello there friend!"
```

## How It Works

### AI Service Architecture

```
Consumer Code
    ↓
ai_api.get_client()
    ↓
    ├── openai_impl.OpenAIClient (Local)
    │       ↓
    │   OpenAI API
    │
    └── ai_adapter.ServiceClient (Remote)
            ↓
        ai_service_client (HTTP)
            ↓
        ai_service (FastAPI)
            ↓
        openai_impl.OpenAIClient
            ↓
        OpenAI API
```

**Key Features:**
- **Conversational Mode**: Returns natural language responses
- **Structured Mode**: Returns JSON matching a provided schema
- **Intent Detection**: Perfect for analyzing user input and extracting structured data
- **Seamless Switching**: Same code works with local or remote implementation

### Mail Client Architecture

```
Consumer Code
    ↓
mail_client_api.get_client()
    ↓
    ├── gmail_client_impl.GmailClient (Local)
    │       ↓
    │   Gmail API
    │
    └── mail_client_adapter.ServiceClient (Remote)
            ↓
        mail_client_service_client (HTTP)
            ↓
        mail_client_service (FastAPI)
            ↓
        gmail_client_impl.GmailClient
            ↓
        Gmail API
```

**Supported Operations:**
- Fetching messages
- Retrieving a single message
- Marking as read
- Deleting messages

## Development Workflow

All commands should be run from the project root with the virtual environment activated.

### Running the Application

**AI Service:**
```bash
# Terminal 1: Start the AI service
uv run uvicorn ai_service.main:app --reload

# Terminal 2: Run the demo
uv run python main.py
```

**Mail Service (Optional):**
```bash
# Start the mail service
uv run uvicorn mail_client_service.main:app --reload --port 8001
```

**Access API Documentation:**
- AI Service: http://127.0.0.1:8000/docs
- Mail Service: http://127.0.0.1:8001/docs

### Running the Toolchain

-   **Linting & Formatting (Ruff):**
    The project uses Ruff with comprehensive rules configured in `pyproject.toml`.
    ```bash
    # Check for issues
    uv run ruff check .
    # Automatically fix issues
    uv run ruff check . --fix
    # Check formatting
    uv run ruff format --check .
    # Apply formatting
    uv run ruff format .
    ```

-   **Static Type Checking (MyPy):**
    ```bash
    uv run mypy src tests
    ```

-   **Testing (Pytest):**

    I'd recommend only running: `uv run pytest src/ tests/ -m "not local_credentials" -v` for simplicity.

    The project uses a comprehensive testing strategy with different test categories.
    ```bash
    # Run all tests (includes unit, integration, and e2e tests)
    uv run pytest

    # Run only unit tests (fast, no external dependencies - from src/ directories)
    uv run pytest src/

    # Run all tests except those requiring local credential files
    uv run pytest src/ tests/ -m "not local_credentials"

    # Run only integration tests (requires environment variables or credentials)
    uv run pytest -m integration

    # Run only end-to-end tests (requires credentials)
    uv run pytest -m e2e

    # Run only CircleCI-compatible tests (CI/CD environment)
    uv run pytest -m circleci

    # Run tests with coverage reporting
    uv run pytest --cov=src --cov-report=term-missing
    ```

### Viewing Documentation


This project uses MkDocs for documentation.
```bash
# Start the live-reloading documentation server
uv run mkdocs serve
```
Open your browser to `http://127.0.0.1:8000` to view the site.

## Testing Infrastructure

The project implements a sophisticated testing strategy designed for both local development and CI/CD environments:

### Test Categories

- **Unit Tests** (`src/*/tests/`): Fast, isolated tests with mocked dependencies
- **Integration Tests** (`tests/integration/`): Tests that verify component interactions
- **End-to-End Tests** (`tests/e2e/`): Full application workflow tests
- **CircleCI Tests**: CI/CD-compatible tests that handle missing credentials gracefully
- **Local Credentials Tests**: Tests that require `credentials.json` or `token.json` files

### Test Markers

The project uses pytest markers to categorize tests:
```bash
@pytest.mark.unit              # Fast unit tests
@pytest.mark.integration       # Integration tests
@pytest.mark.e2e              # End-to-end tests
@pytest.mark.circleci         # CI/CD compatible
@pytest.mark.local_credentials # Requires local auth files
```

### Authentication in Tests

The testing infrastructure handles different authentication scenarios:
- **Local Development**: Uses `credentials.json` and `token.json` files
- **CI/CD Environment**: Uses environment variables (`GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`)
- **Missing Credentials**: Tests fail fast with clear error messages (no hanging)

## Continuous Integration

The project includes a comprehensive CircleCI configuration (`.circleci/config.yml`) with:

- **All Branches**: Unit tests, linting, and CI-compatible tests
- **Main/Develop**: Additional integration tests with real Gmail API calls
- **Artifacts**: Coverage reports, test results, and build summaries

See `docs/circleci-setup.md` for detailed CI/CD setup instructions.

## Deployment

- **Containerization**:  
  The FastAPI `mail_client_service` has been containerized with a production-ready `Dockerfile`.  

- **Fly.io Deployment**:  
  The service is deployed on **Fly.io**, with configuration managed via `fly.toml`.

- **Public Endpoint**:  
  The deployed service is available over HTTPS at:  
  👉 [https://oss-nml.fly.dev/](https://oss-nml.fly.dev/)  

## Development Workflow

### Quick Start
1. **Install dependencies**: `uv sync --all-packages --extra dev`
2. **Run tests**: `uv run pytest tests/ -v` or `uv run pytest src/ tests/ -m "not local_credentials" -v`
3. **Check code quality**: `uv run ruff check . && uv run ruff format --check .`
4. **Fix formatting**: `uv run ruff format .`
5. **View documentation**: `uv run mkdocs serve`

### Best Practices
- Run unit tests (`uv run pytest src/`) during development for fast feedback
- Use integration tests (`uv run pytest -m integration`) to verify component interactions
- Run full test suite (`uv run pytest`) before pushing to ensure CI compatibility
- The CircleCI pipeline provides automated validation on every push