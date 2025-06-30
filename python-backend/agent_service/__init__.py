"""
Customer service agents package.
"""
from .context import CustomerServiceContext, create_initial_context
from .tools import TOOLS_REGISTRY
from .guardrails import GUARDRAILS_REGISTRY
from .instructions import INSTRUCTIONS_REGISTRY
from .hooks import HOOKS_REGISTRY
from .agent_factory import AgentFactory, get_default_agent_name, get_agent_factory

__all__ = [
    "CustomerServiceContext",
    "create_initial_context", 
    "TOOLS_REGISTRY",
    "GUARDRAILS_REGISTRY",
    "INSTRUCTIONS_REGISTRY",
    "HOOKS_REGISTRY",
    "AgentFactory",
    "get_default_agent_name",
    "get_agent_factory",
] 