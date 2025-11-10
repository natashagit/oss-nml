# AI Client Service: A Component-Based Architecture

[![CircleCI](https://circleci.com/gh/ivanearisty/oss-taapp.svg?style=shield)](https://circleci.com/gh/ivanearisty/oss-taapp)
[![Coverage](https://img.shields.io/badge/coverage-85%2B%25-brightgreen)](https://circleci.com/gh/ivanearisty/oss-taapp)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

This repository demonstrates a robust, component-based architecture for building an **AI client service** that provides chat completion capabilities using OpenAI's API with OAuth 2.0 authentication.

The project emphasizes a strict separation of concerns, dependency injection, and a comprehensive, automated toolchain to enforce code quality and best practices.

## Architectural Philosophy

This project is built on the principle of "programming integrated over time." The architecture is designed to combat complexity and ensure the system is maintainable and evolvable.

-   **Component-Based Design:** The system is broken down into distinct, self-contained components. Each component has a single responsibility and can be "forklifted" out of this project to be used in another with minimal effort.
-   **Interface-Implementation Separation:** Every piece of functionality is defined by an abstract **contract** implemented as an ABC (the "what") and fulfilled by a concrete **implementation** (the "how"). This decouples our business logic from specific technologies (like OpenAI).
-   **Dependency Injection:** Implementations are "injected" into the abstract contracts at runtime. This means consumers of the API only ever depend on the stable interface, not the volatile implementation details.

## Core Components

The project is a `uv` workspace containing five primary packages that implement the Adapter Pattern:

1. **`ai_client_api`**: Defines the abstract `Client` base class (ABC) for AI chat operations. This is the contract for what actions an AI client can perform (e.g., `chat_completion`, `chat_completion_stream`).

2. **`openai_client_impl`**: Provides the `OpenAIClient` class, a concrete implementation that uses OpenAI's API to perform chat completions. Includes OAuth 2.0 authentication via Google.

3. **`ai_client_service`**: A FastAPI service that wraps the `ai_client_api` interface and exposes REST endpoints with OAuth 2.0 authentication (`/oauth/authorize`, `/oauth/callback`, `/chat/completions`, `/chat/completions/stream`, `/api-keys`).

4. **`ai_client_adapter`**: Wraps an auto-generated client from the OpenAPI spec and implements the `ai_client_api.Client` interface, making remote service calls feel identical to local library usage.

5. **`ai_client_service_client`**: Auto-generated Python client package (produced with `openapi-python-client`) that provides strongly-typed methods for interacting with the AI service endpoints.

## Project Structure

```
ta-assignment/
├── src/                            # Source packages (uv workspace members)
│   ├── ai_client_api/              # Abstract AI client base class (ABC)
│   ├── openai_client_impl/         # OpenAI-specific client implementation with OAuth
│   ├── ai_client_service/          # FastAPI web service exposing AI Client via REST endpoints
│   ├── ai_client_adapter/          # Adapter wrapping auto-generated AI client to match Client interface
│   └── ai_client_service_client/   # Auto-generated AI client code from OpenAPI
├── tests/                          # Integration and E2E tests
│   ├── integration/                # Component integration tests
│   └── e2e/                        # End-to-end application tests
├── docs/                           # Documentation source files
├── .circleci/                      # CircleCI configuration
├── main.py                         # Main application entry point (AI client demo)
├── Dockerfile                      # Docker configuration for AI service
├── docker-compose.yml              # Docker Compose configuration
├── pyproject.toml                  # Project configuration (dependencies, tools)
├── uv.lock                         # Locked dependency versions
└── .env.example                    # Environment variables template
```

## Project Setup

### 1. Prerequisites

-   Python 3.11 or higher
-   `uv` – A fast, all-in-one Python package manager.
-   Google OAuth credentials (for OAuth authentication)
-   OpenAI API key (for AI operations)

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

3.  **Set Up Google OAuth Credentials:**
    -   Go to [Google Cloud Console](https://console.cloud.google.com/)
    -   Create a new project or select an existing one
    -   Enable Google Identity API or Google+ API
    -   Go to **APIs & Services** → **Credentials**
    -   Create OAuth 2.0 Client ID (Web application)
    -   Add redirect URI: `http://localhost:8000/oauth/callback`
    -   Copy the Client ID and Client Secret

4.  **Set Up Environment Variables:**
    ```bash
    # Copy the example file
    cp .env.example .env
    
    # Edit .env and add your credentials
    GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
    GOOGLE_CLIENT_SECRET=your-google-client-secret
    OAUTH_REDIRECT_URI=http://localhost:8000/oauth/callback
    OPENAI_API_KEY=sk-proj-...
    ```

5.  **Create and Sync the Virtual Environment:**
    This single command creates a `.venv` folder and installs all packages (including workspace members and development tools) defined in `uv.lock`.
    ```bash
    uv sync --all-packages --extra dev
    ```

6.  **Activate the Virtual Environment:**
    ```bash
    # macOS / Linux
    source .venv/bin/activate
    # Windows (PowerShell)
    .venv\Scripts\Activate.ps1
    ```

## How It Works

### Service Layer (`ai_client_service`)
FastAPI app that provides:
- **OAuth 2.0 Authentication**: Google OAuth flow for user authentication
- **Session Management**: Stores user authentication state and API keys in encrypted sessions
- **REST Endpoints**: `/chat/completions`, `/chat/completions/stream`, `/api-keys`, `/oauth/authorize`, `/oauth/callback`

### Architecture Flow
1. **OAuth Authentication**: User authenticates via Google OAuth (`/oauth/authorize` → Google → `/oauth/callback`)
2. **API Key Setup**: Authenticated users set their OpenAI API key via `POST /api-keys` (stored in session)
3. **AI Operations**: Users make chat completion requests via `POST /chat/completions` or `/chat/completions/stream`
4. **Adapter Pattern**: The `ai_client_adapter` wraps the auto-generated client, making remote calls feel like local library usage

### Generated Client (`ai_client_service_client`)
Auto-generated with `openapi-python-client`, providing strongly typed request/response methods for all AI service endpoints.

### Adapter Layer (`ai_client_adapter`)
Wraps the generated client and conforms to `ai_client_api.Client`.  
Consumer code calls `ai_client_api.get_client()` and stays unchanged whether it uses the local OpenAI implementation or the remote service.

### Demo (`main.py`)
Demonstrates AI client operations:
- Chat completions (non-streaming)
- Streaming chat completions
- Multiple model support (GPT-3.5, GPT-4, etc.)

## Development Workflow

All commands should be run from the project root with the virtual environment activated.

### Running the Application

#### AI Client Service

Start the FastAPI AI service (in one terminal):
```bash
# Set required environment variables
export GOOGLE_CLIENT_ID="your-google-client-id"
export GOOGLE_CLIENT_SECRET="your-google-client-secret"
export OAUTH_REDIRECT_URI="http://127.0.0.1:8000/oauth/callback"
export OPENAI_API_KEY="sk-proj-..."

# Start the service
uv run uvicorn ai_client_service.main:app --host 127.0.0.1 --port 8000 --reload
```

**Or use Docker:**
```bash
# Create .env file with required variables
cp .env.example .env
# Edit .env with your credentials

# Build and run
docker-compose up --build -d
```

The AI service will be available at:
- API: http://127.0.0.1:8000
- Documentation: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

#### Running Demo Scripts

To run the AI client demonstration script:
```bash
# Set OPENAI_API_KEY environment variable
export OPENAI_API_KEY="sk-proj-..."

# Run the demo
uv run python main.py
```

The demo script uses the local OpenAI implementation directly (not the service).

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
- **Local Credentials Tests**: Tests that require environment variables or credential files

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
- **Local Development**: Uses environment variables (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OPENAI_API_KEY`)
- **CI/CD Environment**: Uses environment variables configured in CI/CD
- **Missing Credentials**: Tests fail fast with clear error messages (no hanging)

## Continuous Integration

The project includes a comprehensive CircleCI configuration (`.circleci/config.yml`) with:

- **All Branches**: Unit tests, linting, and CI-compatible tests
- **Main/Develop**: Additional integration tests with real API calls
- **Artifacts**: Coverage reports, test results, and build summaries

See `docs/circleci-setup.md` for detailed CI/CD setup instructions.

## Deployment

### AI Client Service

- **Containerization**:  
  The FastAPI `ai_client_service` has been containerized with a production-ready `Dockerfile` and `docker-compose.yml`.

- **Docker Deployment**:  
  The service can be deployed using Docker Compose:
  ```bash
  docker-compose up --build -d
  ```

- **Public Endpoint**:  
  The deployed service is available over HTTPS at:  
  👉 [https://oss-nml.onrender.com](https://oss-nml.onrender.com)

- **Environment Variables**:  
  Required environment variables:
  - `GOOGLE_CLIENT_ID`: Google OAuth Client ID
  - `GOOGLE_CLIENT_SECRET`: Google OAuth Client Secret
  - `OAUTH_REDIRECT_URI`: OAuth redirect URI (default: `http://localhost:8000/oauth/callback`)
  - `OPENAI_API_KEY`: OpenAI API key for the service
  - `SESSION_SECRET_KEY`: (Optional) Secret key for session encryption (auto-generated if not set)

- **Production Considerations**:  
  - Set `HTTPS_ONLY=true` for secure cookies
  - Configure `SESSION_MAX_AGE` for session expiration
  - Use a strong `SESSION_SECRET_KEY`
  - Configure proper OAuth redirect URIs for your domain

## AI Client Service Usage

### Authentication Flow

1. **Initiate OAuth**: Visit `http://localhost:8000/oauth/authorize` or use the Swagger UI
2. **Google Sign-In**: You'll be redirected to Google to sign in
3. **Callback**: Google redirects back to `/oauth/callback` with your user info
4. **Set API Key**: Use `POST /api-keys` to store your OpenAI API key in the session
5. **Use AI Service**: Make requests to `POST /chat/completions` or `/chat/completions/stream`

### Example API Usage

#### Using Swagger UI
1. Start the service: `uv run uvicorn ai_client_service.main:app --host 127.0.0.1 --port 8000 --reload`
2. Open http://127.0.0.1:8000/docs
3. Complete OAuth flow via `/oauth/authorize`
4. Set your API key via `POST /api-keys`
5. Use `POST /chat/completions` to chat with AI

#### Using Python Client

```python
from ai_client_adapter import register
import ai_client_api

# Register the service adapter
register()

# Get client (will use the service adapter)
client = ai_client_api.get_client(user_id="user123")

# Create a chat completion
messages = [
    ai_client_api.models.ChatMessage(role="user", content="Hello!")
]
response = client.chat_completion(messages, model="gpt-3.5-turbo")
print(response.message.content)
```

#### Using Local Implementation

```python
import openai_client_impl
import ai_client_api

# Register the local implementation
openai_client_impl.register()

# Get client (will use local OpenAI implementation)
client = ai_client_api.get_client(user_id="user123")

# Use the client (requires OPENAI_API_KEY environment variable)
messages = [
    ai_client_api.models.ChatMessage(role="user", content="Hello!")
]
response = client.chat_completion(messages, model="gpt-3.5-turbo")
print(response.message.content)
```

## Development Workflow

### Quick Start
1. **Install dependencies**: `uv sync --all-packages --extra dev`
2. **Set up environment**: Copy `.env.example` to `.env` and configure credentials
3. **Run tests**: `uv run pytest src/ tests/ -m "not local_credentials" -v`
4. **Check code quality**: `uv run ruff check . && uv run ruff format --check .`
5. **Fix formatting**: `uv run ruff format .`
6. **View documentation**: `uv run mkdocs serve`

### Best Practices
- Run unit tests (`uv run pytest src/`) during development for fast feedback
- Use integration tests (`uv run pytest -m integration`) to verify component interactions
- Run full test suite (`uv run pytest`) before pushing to ensure CI compatibility
- The CircleCI pipeline provides automated validation on every push
- Test OAuth flow locally before deploying
- Use Docker Compose for consistent deployment environments
