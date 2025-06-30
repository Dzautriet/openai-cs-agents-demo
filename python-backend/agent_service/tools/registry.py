"""
Tool registry for automatic discovery and registration of tools.
This module automatically discovers all tools from the various tool modules.
"""
import importlib
import inspect
from typing import Dict, Any, Callable
from pathlib import Path


def _discover_tools() -> Dict[str, Callable]:
    """
    Automatically discover all tools from tool modules.
    This function scans all Python files in the tools directory and
    finds functions decorated with @function_tool.
    """
    tools = {}
    
    # Get the current directory (tools directory)
    tools_dir = Path(__file__).parent
    
    # List of tool modules to scan
    tool_modules = [
        'customer_service',
        'information', 
        'file_operations',
        'content_generation',
        'web_search',
    ]
    
    for module_name in tool_modules:
        try:
            # Import the module
            module = importlib.import_module(f'agent_service.tools.{module_name}')
            
            # Scan for both functions and FunctionTool objects
            for name, obj in inspect.getmembers(module):
                # Check if this is a FunctionTool object
                if hasattr(obj, 'name') and hasattr(obj, 'description') and hasattr(obj, 'on_invoke_tool'):
                    # This is a FunctionTool object
                    tool_name = obj.name
                    # Store the tool with its source module for categorization
                    obj._source_module = module_name  # Add source module info
                    tools[tool_name] = obj
                elif inspect.isfunction(obj) and name.endswith('_tool') and name != 'function_tool':
                    # This is a regular function that might be a tool
                    tool_name = getattr(obj, 'name', name)
                    tools[tool_name] = obj
                    
        except ImportError as e:
            print(f"Warning: Could not import tool module {module_name}: {e}")
            continue
    
    return tools


def _manual_tool_registry() -> Dict[str, Callable]:
    """
    Manual tool registry as a fallback or for explicit tool registration.
    This is useful when automatic discovery doesn't work or for better control.
    """
    from .customer_service import update_seat, display_seat_map, cancel_flight
    from .information import faq_lookup_tool, flight_status_tool, baggage_tool
    
    return {
        "update_seat": update_seat,
        "display_seat_map": display_seat_map,
        "cancel_flight": cancel_flight,
        "faq_lookup_tool": faq_lookup_tool,
        "flight_status_tool": flight_status_tool,
        "baggage_tool": baggage_tool,
    }


# Create the main tools registry
# Try automatic discovery first, fall back to manual registry
try:
    TOOLS_REGISTRY = _discover_tools()
    if not TOOLS_REGISTRY or len(TOOLS_REGISTRY) <= 1:  # function_tool itself might be discovered
        # If automatic discovery didn't find anything useful, use manual registry
        TOOLS_REGISTRY = _manual_tool_registry()
except Exception as e:
    print(f"Warning: Tool auto-discovery failed, using manual registry: {e}")
    TOOLS_REGISTRY = _manual_tool_registry()


def register_tool(name: str, tool_function: Callable) -> None:
    """
    Manually register a tool in the registry.
    Useful for dynamically adding tools at runtime.
    
    Args:
        name: The name to register the tool under
        tool_function: The tool function to register
    """
    TOOLS_REGISTRY[name] = tool_function


def get_tool(name: str) -> Callable:
    """
    Get a tool by name from the registry.
    
    Args:
        name: The name of the tool to retrieve
        
    Returns:
        The tool function
        
    Raises:
        KeyError: If the tool is not found
    """
    if name not in TOOLS_REGISTRY:
        raise KeyError(f"Tool '{name}' not found in registry. Available tools: {list(TOOLS_REGISTRY.keys())}")
    return TOOLS_REGISTRY[name]


def list_tools() -> Dict[str, str]:
    """
    List all available tools with their descriptions.
    
    Returns:
        Dictionary mapping tool names to their descriptions
    """
    tool_info = {}
    for name, tool_func in TOOLS_REGISTRY.items():
        # Try to get description from docstring or function attributes
        description = getattr(tool_func, 'description', None)
        if not description and tool_func.__doc__:
            description = tool_func.__doc__.split('\n')[0].strip()
        tool_info[name] = description or "No description available"
    
    return tool_info


def get_tools_by_category() -> Dict[str, Dict[str, Callable]]:
    """
    Get tools organized by category based on their module.
    
    Returns:
        Dictionary with categories as keys and tool dictionaries as values
    """
    categories = {
        'customer_service': {},
        'information': {},
        'file_operations': {},
        'content_generation': {},
        'web_search': {},
        'other': {}
    }
    
    for name, tool_func in TOOLS_REGISTRY.items():
        # Try to determine category from stored source module or module name
        source_module = getattr(tool_func, '_source_module', None)
        if source_module:
            category = source_module
        else:
            # Fallback to checking module name
            module_name = getattr(tool_func, '__module__', '')
            category = 'other'
            for cat in categories.keys():
                if cat in module_name:
                    category = cat
                    break
        
        # Make sure category exists
        if category not in categories:
            categories[category] = {}
            
        categories[category][name] = tool_func
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v} 