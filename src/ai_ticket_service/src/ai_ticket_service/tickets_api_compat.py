"""Compatibility layer for trello_ticket_impl import structure.

Their implementation expects to import from 'tickets_api.src.tickets_api'
but our structure is just 'tickets_api'. This module provides the compatibility.
"""

# Re-export everything from tickets_api to match their expected import structure
from tickets_api import *  # noqa: F403, F401

# Create the nested structure they expect
import sys
import tickets_api

# Create tickets_api.src module
if 'tickets_api.src' not in sys.modules:
    import types
    src_module = types.ModuleType('tickets_api.src')
    sys.modules['tickets_api.src'] = src_module
    
    # Create tickets_api.src.tickets_api module that points to our tickets_api
    sys.modules['tickets_api.src.tickets_api'] = tickets_api