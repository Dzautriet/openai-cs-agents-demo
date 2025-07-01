"""
Customer service agents package.
"""
from .context import CustomerServiceContext, create_initial_context, ContextFactory
from .tools import TOOLS_REGISTRY
from .guardrails import GUARDRAILS_REGISTRY
from .instructions import INSTRUCTIONS_REGISTRY
from .hooks import HOOKS_REGISTRY
from .agent_factory import (
    AgentFactory, 
    get_agent_factory, 
    get_default_agent_name,
    create_initial_context_from_config
)

__all__ = [
    "CustomerServiceContext",
    "create_initial_context",  # Legacy function for backward compatibility
    "ContextFactory",
    "TOOLS_REGISTRY",
    "GUARDRAILS_REGISTRY",
    "INSTRUCTIONS_REGISTRY",
    "HOOKS_REGISTRY",
    "AgentFactory",
    "get_agent_factory",
    "get_default_agent_name",
    "create_initial_context_from_config",  # New configurable function
] 