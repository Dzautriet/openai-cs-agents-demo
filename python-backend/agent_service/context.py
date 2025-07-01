"""
Context definitions and factory for customer service agents.
"""
import random
from typing import Dict, Any, Optional, Type, Callable
from pydantic import BaseModel


class CustomerServiceContext(BaseModel):
    """Context for customer service agents."""
    passenger_name: str | None = None
    confirmation_number: str | None = None
    seat_number: str | None = None
    flight_number: str | None = None
    account_number: str | None = None  # Account number associated with the customer


# Context Registry
CONTEXT_REGISTRY: Dict[str, Type[BaseModel]] = {}
CONTEXT_FACTORY_REGISTRY: Dict[str, Callable[..., BaseModel]] = {}


def register_context(name: str, context_class: Type[BaseModel]):
    """Register a context class."""
    CONTEXT_REGISTRY[name] = context_class


def register_context_factory(name: str, factory_function: Callable[..., BaseModel]):
    """Register a context factory function."""
    CONTEXT_FACTORY_REGISTRY[name] = factory_function


def create_customer_service_context(config: Optional[Dict[str, Any]] = None) -> CustomerServiceContext:
    """
    Factory for a new CustomerServiceContext.
    For demo: generates a fake account number.
    In production, this should be set from real user data.
    """
    ctx = CustomerServiceContext()
    
    if config:
        # Apply default values from config
        default_values = config.get("default_values", {})
        if "account_number_range" in default_values:
            range_config = default_values["account_number_range"]
            ctx.account_number = str(random.randint(range_config[0], range_config[1]))
        
        # Apply any initial field values from config
        initial_values = config.get("initial_values", {})
        for field, value in initial_values.items():
            if hasattr(ctx, field):
                setattr(ctx, field, value)
    else:
        # Fallback to original behavior
        ctx.account_number = str(random.randint(10000000, 99999999))
    
    return ctx


def create_initial_context() -> CustomerServiceContext:
    """
    Legacy factory function for backward compatibility.
    This maintains the original API while the system transitions to the new pattern.
    """
    return create_customer_service_context()


# Register default context types
register_context("CustomerServiceContext", CustomerServiceContext)
register_context_factory("create_customer_service_context", create_customer_service_context)


class ContextFactory:
    """Factory for creating contexts from configuration."""
    
    def __init__(self, contexts_config: Optional[Dict[str, Any]] = None):
        """Initialize the context factory with configuration."""
        self.contexts_config = contexts_config or {}
    
    def create_context(self, context_name: str, initial_values: Optional[Dict[str, Any]] = None) -> BaseModel:
        """Create a context instance from configuration."""
        if context_name not in self.contexts_config:
            raise ValueError(f"Unknown context configuration: {context_name}")
        
        context_config = self.contexts_config[context_name]
        factory_function_name = context_config.get("factory_function")
        
        if factory_function_name and factory_function_name in CONTEXT_FACTORY_REGISTRY:
            factory_function = CONTEXT_FACTORY_REGISTRY[factory_function_name]
            
            # Merge initial values with context config
            config_with_values = context_config.copy()
            if initial_values:
                config_with_values.setdefault("initial_values", {}).update(initial_values)
            
            return factory_function(config_with_values)
        
        else:
            # Fallback to direct class instantiation
            class_name = context_config.get("class", "CustomerServiceContext")
            if class_name in CONTEXT_REGISTRY:
                context_class = CONTEXT_REGISTRY[class_name]
                context_instance = context_class()
                
                # Apply initial values if provided
                if initial_values:
                    for field, value in initial_values.items():
                        if hasattr(context_instance, field):
                            setattr(context_instance, field, value)
                
                return context_instance
            else:
                raise ValueError(f"Unknown context class: {class_name}")
    
    def get_context_metadata(self, context_name: str) -> Dict[str, Any]:
        """Get metadata about a context configuration."""
        if context_name not in self.contexts_config:
            raise ValueError(f"Unknown context configuration: {context_name}")
        
        return self.contexts_config[context_name]
    
    def list_contexts(self) -> Dict[str, Dict[str, Any]]:
        """List all available context configurations."""
        return self.contexts_config.copy() 