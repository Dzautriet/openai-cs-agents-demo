"""
API endpoints for the agent service.
"""
import json
import traceback
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import Agent

from agent_service import (
    get_agent_factory,
    create_initial_context,  # Keep for backward compatibility
    create_initial_context_from_config,  # New configurable function
)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    agent_name: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    agent_name: str
    handoffs: List[str]
    error: Optional[str] = None


class AgentInfo(BaseModel):
    name: str
    description: str
    handoffs: List[str]
    tools: List[str]
    input_guardrails: List[str]


class ContextInfo(BaseModel):
    name: str
    description: str
    fields: List[Dict[str, Any]]
    default_values: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Agent Service API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/agents", response_model=List[AgentInfo])
async def list_agents():
    """Get a list of all available agents."""
    try:
        factory = get_agent_factory()
        agents_data = factory.list_agents()
        
        return [
            AgentInfo(
                name=agent["name"],
                description=agent["description"],
                handoffs=agent["handoffs"],
                tools=agent["tools"],
                input_guardrails=agent["input_guardrails"],
            )
            for agent in agents_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@app.get("/contexts", response_model=List[ContextInfo])
async def list_contexts():
    """Get a list of all available context configurations."""
    try:
        factory = get_agent_factory()
        contexts_data = factory.list_contexts()
        
        return [
            ContextInfo(
                name=context_name,
                description=context_config.get("description", ""),
                fields=context_config.get("fields", []),
                default_values=context_config.get("default_values", {}),
            )
            for context_name, context_config in contexts_data.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list contexts: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat requests with agents."""
    try:
        factory = get_agent_factory()
        
        # Get the agent
        if request.agent_name:
            agent = factory.get_agent_by_name(request.agent_name)
        else:
            agent = factory.get_default_agent()
        
                 # Create context - use the new configurable method but fall back to legacy for compatibility
         try:
             ctx = create_initial_context_from_config()
         except Exception:
             # Fallback to legacy method if new method fails
             ctx = create_initial_context()
         
         # Execute the agent with the message (simplified approach)
         response = f"Response from {agent.name}: {request.message}"
        
        # Extract handoff names for the response
        handoff_names = []
        for handoff_item in getattr(agent, "handoffs", []):
            if hasattr(handoff_item, "agent_name"):
                handoff_names.append(handoff_item.agent_name)
            elif hasattr(handoff_item, "name"):
                handoff_names.append(handoff_item.name)
            else:
                handoff_names.append(str(handoff_item))
        
        return ChatResponse(
            response=response,
            agent_name=agent.name,
            handoffs=handoff_names,
        )
    
    except Exception as e:
        # Log the full traceback for debugging
        print(f"Error in chat endpoint: {traceback.format_exc()}")
        
        return ChatResponse(
            response="I apologize, but I encountered an error processing your request.",
            agent_name=request.agent_name or "Unknown",
            handoffs=[],
            error=str(e),
        )


@app.post("/chat/context")
async def create_context(context_name: Optional[str] = None, initial_values: Optional[Dict[str, Any]] = None):
    """Create a new context instance."""
    try:
        factory = get_agent_factory()
        context = factory.create_initial_context(context_name, initial_values)
        
        # Convert to dict for JSON response
        if hasattr(context, 'model_dump'):
            context_dict = context.model_dump()
        elif hasattr(context, 'dict'):
            context_dict = context.dict()
        else:
            context_dict = dict(context)
        
        return {
            "context": context_dict,
            "context_type": type(context).__name__,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create context: {str(e)}")


if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        print("uvicorn not available, run with: poetry run uvicorn api:app --reload")
