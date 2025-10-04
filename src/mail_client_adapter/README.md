# Mail Client Adapter

The **`mail_client_adapter`** package provides an adapter implementation of the abstract `mail_client_api.Client` interface.  
It wraps the auto-generated service client (`mail_client_service_client`) and makes remote service calls feel identical to local library usage.

This allows consumer code to remain unchanged regardless of whether the underlying implementation is:
- **Local**: `gmail_client_impl` (direct Gmail API access)
- **Remote**: `mail_client_service` (FastAPI service) + `mail_client_adapter`

---

## Purpose

- Implements the **Adapter Pattern**:  
  Ensures the auto-generated service client conforms to the `mail_client_api.Client` interface.
- Hides network complexity from consumers:  
  Code that uses `mail_client_api.get_client()` does not need to know if it’s calling Gmail directly or via the FastAPI service.

---

## Usage

First, ensure the **FastAPI service** is running:

```bash
uv run uvicorn mail_client_service.main:app --reload
