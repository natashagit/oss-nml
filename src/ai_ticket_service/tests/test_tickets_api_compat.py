"""Tests for the tickets_api compatibility layer."""

import sys


def test_tickets_api_compat_creates_module_structure() -> None:
    """Test that the compat module creates tickets_api.src in sys.modules."""
    # Remove the modules if they exist to test fresh import
    modules_to_remove = [
        "ai_ticket_service.tickets_api_compat",
        "tickets_api.src",
        "tickets_api.src.tickets_api",
    ]
    for mod in modules_to_remove:
        if mod in sys.modules:
            del sys.modules[mod]

    # Import the compat module - this should create the structure
    import ai_ticket_service.tickets_api_compat  # noqa: F401

    # Verify the modules were created
    assert "tickets_api.src" in sys.modules
    assert "tickets_api.src.tickets_api" in sys.modules

    # Verify we can import from the created structure
    from tickets_api.src.tickets_api import TicketInterface, TicketStatus  # noqa: F401

    # Clean up
    for mod in modules_to_remove:
        if mod in sys.modules:
            del sys.modules[mod]


def test_tickets_api_compat_already_exists() -> None:
    """Test that the compat module doesn't break if tickets_api.src already exists."""
    # Ensure tickets_api.src exists first
    import ai_ticket_service.tickets_api_compat  # noqa: F401

    # Import again - should not raise
    import importlib

    importlib.reload(sys.modules["ai_ticket_service.tickets_api_compat"])

    # Should still work
    from tickets_api.src.tickets_api import TicketInterface  # noqa: F401

    assert "tickets_api.src" in sys.modules
