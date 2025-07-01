# Context Management Refactoring

## Overview

The context management system has been refactored to follow the same low-code, configuration-driven pattern used by the rest of the agent system. This eliminates hard-coded context creation and makes the system more flexible and extensible.

## Key Changes

### Before (Hard-coded)
- Single `CustomerServiceContext` class hard-coded in `context.py`
- Fixed `create_initial_context()` function with embedded logic
- No configuration options for context initialization
- All agents use the same context type

### After (Configuration-driven)
- Context configurations defined in YAML
- Context registry and factory system
- Configurable context creation with default values
- Support for multiple context types
- Backward compatibility maintained

## New Architecture Components

### 1. Context Configuration in YAML

Added to `agents_config.yaml`:

```yaml
# Context configurations
contexts:
  customer_service_context:
    class: "CustomerServiceContext"
    description: "Context for customer service interactions"
    factory_function: "create_customer_service_context"
    default_values:
      account_number_range: [10000000, 99999999]
    fields:
      - name: "passenger_name"
        type: "str"
        optional: true
      - name: "confirmation_number"  
        type: "str"
        optional: true
      # ... additional fields

# Default context configuration
default_context: "customer_service_context"
```

### 2. Context Registry System

New components in `context.py`:

- **`CONTEXT_REGISTRY`**: Maps context names to context classes
- **`CONTEXT_FACTORY_REGISTRY`**: Maps factory function names to factory functions
- **`register_context()`**: Register new context classes
- **`register_context_factory()`**: Register new factory functions

### 3. Context Factory Class

The `ContextFactory` class provides:

- **`create_context()`**: Create context instances from configuration
- **`get_context_metadata()`**: Get metadata about context configurations
- **`list_contexts()`**: List all available context configurations

### 4. Enhanced Agent Factory

The `AgentFactory` now includes:

- **`create_initial_context()`**: Create contexts using the new system
- **`get_context_factory()`**: Access to the context factory
- **`list_contexts()`**: List available context configurations

## Usage Examples

### Creating Contexts with Default Configuration

```python
from agent_service import get_agent_factory

factory = get_agent_factory()

# Create context using default configuration
context = factory.create_initial_context()

# Create context with specific configuration
context = factory.create_initial_context("customer_service_context")

# Create context with initial values
context = factory.create_initial_context(
    "customer_service_context",
    {"passenger_name": "John Doe", "flight_number": "AA123"}
)
```

### Using the New Configuration Function

```python
from agent_service import create_initial_context_from_config

# Create context using global factory instance
context = create_initial_context_from_config()

# With specific configuration and values
context = create_initial_context_from_config(
    context_name="customer_service_context",
    initial_values={"confirmation_number": "ABC123"}
)
```

### Adding New Context Types

1. **Define the Context Class:**

```python
# In context.py
class NewServiceContext(BaseModel):
    service_type: str | None = None
    priority_level: str | None = None

# Register the new context
register_context("NewServiceContext", NewServiceContext)
```

2. **Create a Factory Function:**

```python
def create_new_service_context(config: Optional[Dict[str, Any]] = None) -> NewServiceContext:
    ctx = NewServiceContext()
    
    if config:
        default_values = config.get("default_values", {})
        if "default_priority" in default_values:
            ctx.priority_level = default_values["default_priority"]
    
    return ctx

register_context_factory("create_new_service_context", create_new_service_context)
```

3. **Add to YAML Configuration:**

```yaml
contexts:
  new_service_context:
    class: "NewServiceContext"
    description: "Context for new service type interactions"
    factory_function: "create_new_service_context"
    default_values:
      default_priority: "standard"
    fields:
      - name: "service_type"
        type: "str"
        optional: true
      - name: "priority_level"
        type: "str"
        optional: true
```

## API Enhancements

### New Endpoints

- **`GET /contexts`**: List all available context configurations
- **`POST /chat/context`**: Create context instances programmatically

### Enhanced Chat Endpoint

The `/chat` endpoint now uses the configurable context system but maintains backward compatibility.

## Migration Guide

### For Existing Code

The refactoring maintains full backward compatibility:

```python
# This still works exactly as before
from agent_service import create_initial_context
context = create_initial_context()
```

### For New Development

Use the new configurable approach:

```python
# Recommended for new code
from agent_service import create_initial_context_from_config
context = create_initial_context_from_config()
```

## Benefits

1. **Consistency**: Context management now follows the same pattern as agents, tools, and guardrails
2. **Flexibility**: Easy to create different context types for different use cases
3. **Configuration**: Context behavior can be modified without code changes
4. **Extensibility**: New context types can be added via configuration
5. **Maintainability**: Clear separation between context definitions and creation logic
6. **Backward Compatibility**: Existing code continues to work unchanged

## Configuration Schema

### Context Configuration Properties

- **`class`**: Name of the context class (must be registered)
- **`description`**: Human-readable description
- **`factory_function`**: Name of the factory function (optional)
- **`default_values`**: Default values to apply during creation
- **`fields`**: Metadata about context fields (for documentation/UI)

### Field Properties

- **`name`**: Field name
- **`type`**: Field type (string representation)
- **`optional`**: Whether the field is optional
- **`description`**: Field description (optional)

## Future Enhancements

This architecture enables future enhancements such as:

- Dynamic context validation based on configuration
- Context field type checking and conversion
- Context inheritance and composition
- Agent-specific context configurations
- Runtime context schema validation
- Context serialization/deserialization customization

## Testing

The refactoring maintains all existing functionality while adding new capabilities. Test both old and new patterns:

```python
# Test backward compatibility
def test_legacy_context_creation():
    ctx = create_initial_context()
    assert ctx.account_number is not None

# Test new configuration system
def test_configurable_context_creation():
    ctx = create_initial_context_from_config(
        initial_values={"passenger_name": "Test User"}
    )
    assert ctx.passenger_name == "Test User"
```