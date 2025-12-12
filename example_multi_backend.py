#!/usr/bin/env python3
"""Example demonstrating multi-backend ticket management with AI."""

import os
import requests
import json

# Configuration
AI_SERVICE_URL = "http://127.0.0.1:8002"

def test_backend(backend_name: str, test_cases: list[str]) -> None:
    """Test a specific backend with various commands."""
    print(f"\n{'='*50}")
    print(f"Testing {backend_name.upper()} Backend")
    print(f"{'='*50}")
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{user_input}'")
        
        response = requests.post(
            f"{AI_SERVICE_URL}/command",
            json={
                "user_input": user_input,
                "backend": backend_name
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Backend Status: {result['backend_status']}")
            print(f"   AI Result: {result['ai_result']}")
            if result['ticket_result']:
                print(f"   Ticket Result: {json.dumps(result['ticket_result'], indent=2)}")
            else:
                print("   Ticket Result: None")
        else:
            print(f"   Error: {response.status_code} - {response.text}")

def main():
    """Run multi-backend demonstration."""
    print("Multi-Backend AI Ticket Service Demo")
    print("====================================")
    
    # Check service health
    try:
        health_response = requests.get(f"{AI_SERVICE_URL}/health")
        if health_response.status_code == 200:
            print(f"✓ AI Ticket Service is running: {health_response.json()}")
        else:
            print(f"✗ Service health check failed: {health_response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to AI service at {AI_SERVICE_URL}")
        print("  Make sure to start the service with:")
        print("  uv run uvicorn ai_ticket_service.main:app --reload --port 8002")
        return
    
    # Test cases for both backends
    test_cases = [
        "Create a ticket to fix the login redirect bug",
        "Create a high priority ticket for database optimization", 
        "Find all tickets about bugs",
        "Search for tickets related to login",
        "Create a ticket to update the user interface",
    ]
    
    # Test Google Tasks backend
    test_backend("google_tasks", test_cases)
    
    # Test Trello backend  
    test_backend("trello", test_cases)
    
    print(f"\n{'='*50}")
    print("Demo Complete!")
    print("="*50)
    print("\nBackend Configuration:")
    print("Google Tasks:")
    print("  - TASKS_INTERACTIVE=false (or true for OAuth)")
    print("  - TASKS_CLIENT_ID, TASKS_CLIENT_SECRET, TASKS_REFRESH_TOKEN")
    print("\nTrello:")
    print("  - TRELLO_TOKEN=your_trello_token")
    print("  - TRELLO_BOARD_ID=your_board_id")
    print("  - Optional: TRELLO_TODO_LIST, TRELLO_IN_PROGRESS_LIST, TRELLO_DONE_LIST")

if __name__ == "__main__":
    main()