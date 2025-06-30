"""
Agent factory for creating agents from YAML configuration.
"""
import os
import yaml
from typing import Dict, Any, List
from pathlib import Path

from agents import Agent, handoff
from .context import CustomerServiceContext
from .tools import TOOLS_REGISTRY
from .guardrails import GUARDRAILS_REGISTRY
from .instructions import INSTRUCTIONS_REGISTRY
from .hooks import HOOKS_REGISTRY


class AgentFactory:
    """Factory for creating agents from YAML configuration."""
    
    def __init__(self, config_path: str = None):
        """Initialize the factory with a configuration file."""
        if config_path is None:
            # Default to agents_config.yaml in the same directory as this file
            config_path = Path(__file__).parent.parent / "agents_config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._agents_cache: Dict[str, Agent[CustomerServiceContext]] = {}
        self._agents_built = False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the YAML configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Agent configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")
    
    def _get_tools(self, tool_names: List[str]) -> List:
        """Get tool objects from tool names."""
        tools = []
        for tool_name in tool_names:
            if tool_name in TOOLS_REGISTRY:
                tools.append(TOOLS_REGISTRY[tool_name])
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        return tools
    
    def _get_guardrails(self, guardrail_names: List[str]) -> List:
        """Get guardrail objects from guardrail names."""
        guardrails = []
        for guardrail_name in guardrail_names:
            if guardrail_name in GUARDRAILS_REGISTRY:
                guardrails.append(GUARDRAILS_REGISTRY[guardrail_name])
            else:
                raise ValueError(f"Unknown guardrail: {guardrail_name}")
        return guardrails
    
    def _get_instructions_function(self, function_name: str):
        """Get instructions function from function name."""
        if function_name in INSTRUCTIONS_REGISTRY:
            return INSTRUCTIONS_REGISTRY[function_name]
        else:
            raise ValueError(f"Unknown instructions function: {function_name}")
    
    def _create_agent(self, agent_id: str, agent_config: Dict[str, Any]) -> Agent[CustomerServiceContext]:
        """Create a single agent from configuration."""
        # Get basic properties
        name = agent_config["name"]
        model = agent_config["model"]
        handoff_description = agent_config.get("handoff_description", "")
        
        # Get instructions function
        instructions_function_name = agent_config.get("instructions_function")
        instructions = None
        if instructions_function_name:
            instructions = self._get_instructions_function(instructions_function_name)
        
        # Get tools
        tool_names = agent_config.get("tools", [])
        tools = self._get_tools(tool_names)
        
        # Get guardrails
        guardrail_names = agent_config.get("input_guardrails", [])
        input_guardrails = self._get_guardrails(guardrail_names)
        
        # Create the agent (handoffs will be set up later)
        agent = Agent[CustomerServiceContext](
            name=name,
            model=model,
            handoff_description=handoff_description,
            instructions=instructions,
            tools=tools,
            input_guardrails=input_guardrails,
        )
        
        return agent
    
    def _setup_handoffs(self):
        """Set up handoffs between agents after all agents are created."""
        agents_config = self.config.get("agents", {})
        
        for agent_id, agent_config in agents_config.items():
            if agent_id not in self._agents_cache:
                continue
                
            source_agent = self._agents_cache[agent_id]
            handoff_configs = agent_config.get("handoffs", [])
            
            handoffs = []
            for handoff_config in handoff_configs:
                target_agent_id = handoff_config["agent"]
                
                if target_agent_id not in self._agents_cache:
                    raise ValueError(f"Unknown target agent in handoff: {target_agent_id}")
                
                target_agent = self._agents_cache[target_agent_id]
                
                # Check if there's an on_handoff hook
                on_handoff_name = handoff_config.get("on_handoff")
                if on_handoff_name:
                    if on_handoff_name in HOOKS_REGISTRY:
                        on_handoff_func = HOOKS_REGISTRY[on_handoff_name]
                        handoffs.append(handoff(agent=target_agent, on_handoff=on_handoff_func))
                    else:
                        raise ValueError(f"Unknown handoff hook: {on_handoff_name}")
                else:
                    handoffs.append(target_agent)
            
            source_agent.handoffs = handoffs
    
    def build_agents(self) -> Dict[str, Agent[CustomerServiceContext]]:
        """Build all agents from configuration."""
        if self._agents_built:
            return self._agents_cache
        
        agents_config = self.config.get("agents", {})
        
        # First pass: create all agents
        for agent_id, agent_config in agents_config.items():
            agent = self._create_agent(agent_id, agent_config)
            self._agents_cache[agent_id] = agent
        
        # Second pass: set up handoffs
        self._setup_handoffs()
        
        self._agents_built = True
        return self._agents_cache
    
    def get_agent(self, agent_id: str) -> Agent[CustomerServiceContext]:
        """Get a specific agent by ID."""
        if not self._agents_built:
            self.build_agents()
        
        if agent_id not in self._agents_cache:
            raise ValueError(f"Unknown agent: {agent_id}")
        
        return self._agents_cache[agent_id]
    
    def get_agent_by_name(self, name: str) -> Agent[CustomerServiceContext]:
        """Get a specific agent by name."""
        if not self._agents_built:
            self.build_agents()
        
        for agent in self._agents_cache.values():
            if agent.name == name:
                return agent
        
        raise ValueError(f"Agent not found with name: {name}")
    
    def get_default_agent(self) -> Agent[CustomerServiceContext]:
        """Get the default/entry agent."""
        default_agent_id = self.config.get("default_agent")
        if not default_agent_id:
            raise ValueError("No default agent specified in configuration")
        
        return self.get_agent(default_agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """Get a list of all agents with their metadata for the API."""
        if not self._agents_built:
            self.build_agents()
        
        agents_list = []
        for agent in self._agents_cache.values():
            # Extract handoff agent names
            handoff_names = []
            for handoff_item in getattr(agent, "handoffs", []):
                if hasattr(handoff_item, "agent_name"):
                    handoff_names.append(handoff_item.agent_name)
                elif hasattr(handoff_item, "name"):
                    handoff_names.append(handoff_item.name)
                else:
                    handoff_names.append(str(handoff_item))
            
            # Extract tool names
            tool_names = []
            for tool in getattr(agent, "tools", []):
                if hasattr(tool, "name"):
                    tool_names.append(tool.name)
                elif hasattr(tool, "__name__"):
                    tool_names.append(tool.__name__)
                else:
                    tool_names.append(str(tool))
            
            # Extract guardrail names
            guardrail_names = []
            for guardrail in getattr(agent, "input_guardrails", []):
                if hasattr(guardrail, "name") and isinstance(guardrail.name, str):
                    guardrail_names.append(guardrail.name)
                elif hasattr(guardrail, "guardrail_function") and hasattr(guardrail.guardrail_function, "__name__"):
                    name = guardrail.guardrail_function.__name__.replace("_", " ").title()
                    guardrail_names.append(name)
                elif hasattr(guardrail, "__name__"):
                    name = guardrail.__name__.replace("_", " ").title()
                    guardrail_names.append(name)
                else:
                    guardrail_names.append(str(guardrail))
            
            agents_list.append({
                "name": agent.name,
                "description": getattr(agent, "handoff_description", ""),
                "handoffs": handoff_names,
                "tools": tool_names,
                "input_guardrails": guardrail_names,
            })
        
        return agents_list


# Global factory instance
_factory_instance = None


def get_agent_factory() -> AgentFactory:
    """Get the global agent factory instance."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = AgentFactory()
    return _factory_instance


def get_default_agent_name() -> str:
    """Get the name of the default agent."""
    factory = get_agent_factory()
    default_agent = factory.get_default_agent()
    return default_agent.name 