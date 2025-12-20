# Architecture

The HW3 system integrates chat, AI, and ticketing into a single pipeline:

Chat -> AI intent extraction -> Ticket backend -> AI formatting -> Chat response

## Core components

- `ai_ticket_service`: Orchestration service and `/chat/command` API.
- `chat_client_api` + `discord_client_impl`: Chat interface and Discord implementation.
- `ai_api` + `openai_impl`: AI contract and OpenAI-backed implementation.
- `tickets_api` + `tickets_client_impl`: Ticket contract and Google Tasks backend.
- `trello_ticket_impl`: Trello backend (configurable via env).
- `ai_ticket_adapter` + `ai_ticket_service_client`: Adapter and generated client for HTTP calls.

## Component layout

Every workspace component lives under `src/<component_name>/` and represents either an abstract
contract implemented as an ABC or a concrete implementation.

## Directory Layout
```
<component_name>/
├── pyproject.toml
├── README.md
├── src/<component_name>/
│   ├── __init__.py
│   └── _impl.py        # only for implementations
└── tests/              # optional component-scoped tests
```

## `pyproject.toml` Checklist
- `[project]`: align `name` with the folder, set `version`, `description`, `readme = "README.md"`, `requires-python = ">=3.11"`, and list direct dependencies.
- `[build-system]`: keep `hatchling` as the backend.
- `[tool.uv.sources]`: declare workspace dependencies when another component is required.

## README Expectations
Document, at minimum: overview, scope, exposed interfaces, usage pattern, and component dependencies. Keep examples using absolute imports.

## Implementation Notes (`_impl.py`)
Place concrete classes here so `__init__.py` can focus on exports and dependency injection wiring.

## Package Initialisation (`__init__.py`)
- Contract packages: define the ABC and `get_*` factory that raises `NotImplementedError`.
- Implementation packages: import the contract, expose factories like `get_*_impl`, and rebind the factory (e.g., `contract.get_* = get_*_impl`). Use `__all__` for any public symbols.

## Testing
Component-level tests belong in `tests/` within each package. Integration and E2E tests live under
the top-level `tests/` directory and exercise the AI-ticket-chat workflow.
