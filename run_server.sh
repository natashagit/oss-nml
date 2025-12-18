#!/bin/bash

# AI Ticket Service Runner
# This script starts the AI Ticket Service with the correct command

echo "Starting AI Ticket Service..."
echo "Server will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the service with development extras and reload
uv run --extra dev uvicorn ai_ticket_service.main:app --reload --port 8000