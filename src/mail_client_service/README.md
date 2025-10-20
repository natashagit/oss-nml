# Mail Client Service

The **`mail_client_service`** package implements the **service layer** for the mail client.  
It exposes the `mail_client_api.Client` interface over HTTP using **FastAPI**.  

This allows the mail client to run as a standalone service process, while consumers interact with it transparently through the adapter.

---

## Purpose

- Wrap the `mail_client_api.Client` interface in a RESTful API.  
- Act as a thin layer: no business logic is re-implemented here.  
- Provide endpoints that correspond directly to the methods of the `Client` interface.  

---

## Endpoints

The service exposes the following REST API endpoints:

- `GET /messages`  
  Fetch a list of message summaries.  

- `GET /messages/{message_id}`  
  Fetch full detail of a single message.  

- `POST /messages/{message_id}/mark-as-read`  
  Mark a message as read.  

- `DELETE /messages/{message_id}`  
  Delete a message.  

- `GET /health`  
  Health check endpoint for monitoring and CI.

---

## Running the Service

Start the FastAPI application using **uvicorn**:

```bash
uv run uvicorn mail_client_service.main:app --reload
