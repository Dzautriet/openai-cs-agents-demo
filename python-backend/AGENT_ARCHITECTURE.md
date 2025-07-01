# Agent Architecture Documentation

## Overview

The agent system has been refactored to use a factory pattern with YAML configuration files. This makes it easy to scale up and add new agents without modifying the core codebase.

## Directory Structure

```
python-backend/
├── agent_service/                 # Main agent service package
│   ├── __init__.py               # Package exports
│   ├── context.py                # Context definitions
│   ├── tools.py                  # Tool definitions and registry
│   ├── guardrails.py             # Guardrail definitions and registry
│   ├── instructions.py           # Instruction functions and registry
│   ├── hooks.py                  # Handoff hook functions and registry
│   └── agent_factory.py          # Agent factory and configuration loader
├── agents_config.yaml            # Main agent configuration file
├── example_new_agent.yaml        # Example of adding new agents
├── main.py                       # Main module (now uses factory)
├── api.py                        # FastAPI application
└── pyproject.toml                # Poetry dependencies (includes PyYAML)
```

## Key Components

### 1. Agent Factory (`agent_service/agent_factory.py`)

The `AgentFactory` class is responsible for:
- Loading YAML configuration files
- Creating agent instances from configuration
- Setting up handoff relationships between agents
- Providing agent lookup and metadata functions

### 2. Configuration File (`agents_config.yaml`)

Defines all agents and their properties:
- Basic agent properties (name, model, description)
- Tools to be attached to each agent
- Guardrails to be applied
- Handoff relationships and hooks
- Instructions function references

### 3. Registries

Each component type has a registry for easy lookup:
- `TOOLS_REGISTRY`: Maps tool names to tool functions
- `GUARDRAILS_REGISTRY`: Maps guardrail names to guardrail functions  
- `INSTRUCTIONS_REGISTRY`: Maps instruction names to instruction functions
- `HOOKS_REGISTRY`: Maps hook names to hook functions

## How to Add New Agents

### Step 1: Add Tools (if needed)

Add new tools to `agent_service/tools.py`:

```python
@function_tool(name_override="new_tool", description_override="Description")
async def new_tool_function(param: str) -> str:
    """New tool implementation."""
    return "result"

# Add to registry
TOOLS_REGISTRY["new_tool"] = new_tool_function
```

### Step 2: Add Instructions Function

Add instruction function to `agent_service/instructions.py`:

```python
def new_agent_instructions(
    run_context: RunContextWrapper[CustomerServiceContext], 
    agent: Agent[CustomerServiceContext]
) -> str:
    return "Agent instructions here"

# Add to registry  
INSTRUCTIONS_REGISTRY["new_agent_instructions"] = new_agent_instructions
```

### Step 3: Add to Configuration

Add the new agent to `agents_config.yaml`:

```yaml
agents:
  new_agent:
    name: "New Agent"
    model: "gpt-4.1"
    handoff_description: "Description for handoffs"
    instructions_function: "new_agent_instructions"
    handoffs:
      - agent: "triage_agent"
    tools:
      - "new_tool"
    input_guardrails:
      - "relevance_guardrail"
      - "jailbreak_guardrail"
```

### Step 4: Update Triage Agent (if needed)

If the new agent should be accessible from the triage agent, add it to the triage agent's handoffs in the YAML config.

## Frontend Discovery

The frontend discovers agents through the `/chat` API endpoint, which returns agent metadata including:
- Agent names and descriptions
- Available handoffs for each agent
- Tools attached to each agent
- Active guardrails

The API uses `factory.list_agents()` to build this metadata dynamically from the loaded configuration.

## Benefits of This Architecture

1. **Scalability**: Easy to add new agents without code changes
2. **Maintainability**: Clear separation of concerns
3. **Configuration Management**: All agent definitions in one place
4. **Flexibility**: Can easily modify agent properties, tools, and relationships
5. **Testability**: Factory pattern makes testing easier
6. **Backward Compatibility**: Existing code still works through exports in `main.py`

## Migration Notes

The refactoring maintains backward compatibility:
- `main.py` exports individual agents for existing imports
- API endpoints work unchanged
- Frontend receives the same agent metadata format

The main change is that agents are now created dynamically from configuration rather than being hard-coded in Python files. 