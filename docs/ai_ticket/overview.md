# AI Ticket Orchestration

The AI Ticket service is the core HW3 orchestration layer. It routes chat input through an AI
router, executes ticket actions on a pluggable backend, and formats the response back to chat.

Workflow:
User input -> AI intent extraction -> Ticket backend -> AI formatting -> Chat response

Live docs: https://oss-nml.onrender.com/docs

Key endpoints:
- `POST /chat/command` for chat-driven ticket actions
- `GET /health` for liveness
