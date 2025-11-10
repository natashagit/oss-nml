# Component Definition

Every workspace component lives under `src/<component_name>/` and represents either an abstract contract implemented as an ABC or a concrete implementation.

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

## AI Service Components

The AI client service consists of five main components:

1. **`ai_client_api`**: Abstract contract defining the `Client` ABC
2. **`openai_client_impl`**: Concrete implementation using OpenAI's API
3. **`ai_client_service`**: FastAPI service exposing REST endpoints
4. **`ai_client_adapter`**: Adapter wrapping the generated service client
5. **`ai_client_service_client`**: Auto-generated client from OpenAPI spec

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
Component-level tests belong in `tests/`. Target the public interface, use mocks to isolate external services, and keep fixtures local to the component.
