# Tools Organization Guide

## Overview

The tools system has been reorganized into a scalable directory structure that makes it easy to add new tools by category. Tools are automatically discovered and registered, making the system highly extensible.

## Directory Structure

```
agent_service/tools/
├── __init__.py                 # Main tools package exports
├── registry.py                 # Tool discovery and registration system
├── customer_service.py         # Customer service specific tools
├── information.py              # Information lookup tools
├── file_operations.py          # File reading/writing tools (placeholder)
├── content_generation.py       # Image/slide generation tools (placeholder)
└── web_search.py              # Web search and API tools (placeholder)
```

## Tool Categories

### 1. Customer Service Tools (`customer_service.py`)
Tools that handle direct customer service actions:
- `update_seat` - Update customer seat assignments
- `display_seat_map` - Show interactive seat map
- `cancel_flight` - Cancel flight bookings

### 2. Information Tools (`information.py`)
Tools that provide information to customers:
- `faq_lookup_tool` - Lookup frequently asked questions
- `flight_status_tool` - Get flight status information
- `baggage_tool` - Lookup baggage policies and fees

### 3. Future Tool Categories (Placeholders)
- **File Operations**: File reading, document creation, data processing
- **Content Generation**: Image generation, slide creation, document formatting
- **Web Search**: Web searches, API calls, external data retrieval

## How to Add New Tools

### Step 1: Choose the Right Category

Determine which category your tool belongs to:
- **Customer Service**: Direct actions that modify customer data
- **Information**: Tools that retrieve and provide information
- **File Operations**: File handling and processing
- **Content Generation**: Creating new content (images, documents, etc.)
- **Web Search**: External data retrieval and API calls

### Step 2: Add Your Tool Function

Add your tool to the appropriate category file. For example, to add a web search tool:

```python
# In agent_service/tools/web_search.py

@function_tool(
    name_override="web_search_tool",
    description_override="Search the web for information."
)
async def web_search_tool(query: str, num_results: int = 5) -> str:
    """Search the web for information."""
    # Your implementation here
    # This could integrate with Google Search API, Bing API, etc.
    
    # Example implementation:
    import requests
    
    # Mock implementation - replace with actual search API
    results = f"Found {num_results} results for '{query}'"
    return results
```

### Step 3: Register the Tool (Automatic)

The tool will be automatically discovered and registered when you:

1. **Import the tool**: The registry automatically scans tool modules
2. **Follow naming conventions**: Functions ending in `_tool` or decorated with `@function_tool`
3. **Place in correct module**: Tools are categorized by their module location

### Step 4: Add to Agent Configuration

Update your `agents_config.yaml` to assign the tool to relevant agents:

```yaml
agents:
  research_agent:
    name: "Research Agent"
    model: "gpt-4.1"
    handoff_description: "An agent that can search for information online."
    instructions_function: "research_instructions"
    tools:
      - "web_search_tool"  # Your new tool
      - "faq_lookup_tool"
    input_guardrails:
      - "relevance_guardrail"
```

### Step 5: Add Instructions Function (if needed)

If you're creating a new agent, add an instructions function:

```python
# In agent_service/instructions.py

def research_instructions(
    run_context: RunContextWrapper[CustomerServiceContext], 
    agent: Agent[CustomerServiceContext]
) -> str:
    return f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a research agent. Use web search tools to find information 
    and provide helpful answers to customer questions.
    """

# Add to registry
INSTRUCTIONS_REGISTRY["research_instructions"] = research_instructions
```

## Advanced Tool Features

### Tool with Context Access

Tools can access and modify the customer context:

```python
@function_tool
async def update_customer_info(
    context: RunContextWrapper[CustomerServiceContext], 
    field: str, 
    value: str
) -> str:
    """Update customer information in the context."""
    setattr(context.context, field, value)
    return f"Updated {field} to {value}"
```

### Tool with External Dependencies

For tools that need external APIs or libraries:

```python
# Add dependencies to pyproject.toml first
# [tool.poetry.dependencies]
# requests = "^2.31.0"
# openai = "^1.0.0"

@function_tool(
    name_override="generate_image_tool",
    description_override="Generate an image from a text description."
)
async def generate_image_tool(description: str, style: str = "realistic") -> str:
    """Generate an image from a text description."""
    import openai
    
    # Example using OpenAI DALL-E
    response = openai.images.generate(
        prompt=f"{description} in {style} style",
        n=1,
        size="1024x1024"
    )
    
    image_url = response.data[0].url
    return f"Generated image: {image_url}"
```

## Tool Registry Functions

The registry provides several utility functions:

```python
from agent_service.tools.registry import (
    list_tools, 
    get_tools_by_category, 
    register_tool,
    get_tool
)

# List all available tools
tools_info = list_tools()
print(tools_info)

# Get tools organized by category
categorized_tools = get_tools_by_category()
print(categorized_tools)

# Manually register a tool at runtime
register_tool("my_custom_tool", my_tool_function)

# Get a specific tool
tool_func = get_tool("web_search_tool")
```

## Best Practices

1. **Naming**: Use descriptive names ending in `_tool`
2. **Documentation**: Include clear docstrings and parameter descriptions
3. **Error Handling**: Handle errors gracefully and return meaningful messages
4. **Type Hints**: Use proper type hints for better IDE support
5. **Testing**: Test tools independently before integrating with agents
6. **Dependencies**: Add external dependencies to `pyproject.toml`
7. **Security**: Validate inputs and sanitize outputs for security

## Example: Adding a Complete New Tool Category

Let's say you want to add database tools:

1. **Create the module**:
```python
# agent_service/tools/database.py

@function_tool(
    name_override="query_database_tool",
    description_override="Query the customer database."
)
async def query_database_tool(query: str) -> str:
    """Query the customer database safely."""
    # Implementation with proper SQL injection protection
    return "Query results here"
```

2. **Update the registry** to include the new module:
```python
# In agent_service/tools/registry.py
tool_modules = [
    'customer_service',
    'information', 
    'file_operations',
    'content_generation',
    'web_search',
    'database',  # Add your new category
]
```

3. **Update the tools package**:
```python
# In agent_service/tools/__init__.py
from .database import *

__all__ = [
    # ... existing tools ...
    "query_database_tool",
]
```

The reorganized tools system provides a clean, scalable foundation for adding any type of tool your agents might need! 