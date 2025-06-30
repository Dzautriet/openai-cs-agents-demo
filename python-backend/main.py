"""
Main module for airline customer service agents.
This module now uses a factory pattern to create agents from YAML configuration.
"""
from agent_service import get_agent_factory, create_initial_context, get_default_agent_name

# Initialize the agent factory and build all agents
factory = get_agent_factory()
agents = factory.build_agents()

# Export individual agents for backward compatibility
triage_agent = factory.get_agent("triage_agent")
faq_agent = factory.get_agent("faq_agent") 
seat_booking_agent = factory.get_agent("seat_booking_agent")
flight_status_agent = factory.get_agent("flight_status_agent")
cancellation_agent = factory.get_agent("cancellation_agent")

# Export the factory and helper functions
__all__ = [
    "factory",
    "agents",
    "triage_agent",
    "faq_agent",
    "seat_booking_agent", 
    "flight_status_agent",
    "cancellation_agent",
    "create_initial_context",
    "get_default_agent_name",
] 