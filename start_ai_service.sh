#!/bin/bash

# AI Ticket Service Startup Script
# Copy .env.example to .env and fill in your actual API keys

echo "Starting AI Ticket Service..."
echo "Make sure you have set the following environment variables:"
echo "- OPENAI_API_KEY"
echo "- TRELLO_API_KEY"
echo "- TRELLO_API_SECRET" 
echo "- TRELLO_TOKEN"
echo "- TRELLO_BOARD_ID"
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "Loading environment from .env file..."
    source .env
else
    echo "⚠️  No .env file found. Copy .env.example to .env and add your credentials."
fi

echo "Starting service on port 8003..."
uv run uvicorn ai_ticket_service.main:app --reload --port 8003