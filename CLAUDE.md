# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend (Next.js)
```bash
cd ui
npm run dev          # Start both frontend and backend simultaneously
npm run dev:next     # Start only the frontend on port 3000
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Lint the code
```

### Backend (Python with Poetry)
```bash
cd python-backend
poetry install       # Install dependencies
poetry shell         # Activate virtual environment
poetry run python start.py            # Start backend server
poetry run uvicorn api:app --reload    # Alternative start command
poetry run black .   # Format code
poetry run isort .   # Sort imports
poetry run mypy .    # Type checking
poetry run pytest   # Run tests
```

### Testing
- Python tests: `poetry run pytest` (in python-backend/)
- Frontend linting: `npm run lint` (in ui/)
- No specific test framework is configured for frontend

## Architecture Overview

This is a customer service agents demo built with the OpenAI Agents SDK. The system uses a multi-agent architecture where specialized agents handle different customer service tasks.

### High-Level Structure
- **Frontend**: Next.js application with TypeScript, Tailwind CSS, and React components for chat interface and agent visualization
- **Backend**: FastAPI Python server using OpenAI Agents SDK with a factory pattern for agent configuration
- **Agent System**: YAML-configured agents with tools, guardrails, and handoff relationships

### Key Architectural Patterns

#### Agent Factory Pattern
Agents are created dynamically from YAML configuration (`agents_config.yaml`) rather than hard-coded. This allows easy scaling and modification without code changes.

#### Modular Tool System
Tools are organized by category in `python-backend/agent_service/tools/`:
- `customer_service.py` - Direct customer actions (seat updates, cancellations)
- `information.py` - Information retrieval (FAQ, flight status)
- `registry.py` - Automatic tool discovery and registration

#### Registry-Based Architecture
Four main registries provide loose coupling:
- `TOOLS_REGISTRY` - Maps tool names to functions
- `GUARDRAILS_REGISTRY` - Maps guardrail names to functions
- `INSTRUCTIONS_REGISTRY` - Maps instruction names to functions
- `HOOKS_REGISTRY` - Maps hook names to handoff functions

### Agent Flow
1. **Triage Agent** - Entry point that routes requests to specialist agents
2. **Specialist Agents** - Handle specific tasks (seat booking, cancellations, FAQ, flight status)
3. **Guardrails** - Applied to all agents (relevance checking, jailbreak protection)
4. **Context Management** - Customer context shared across agent handoffs

## Environment Configuration

### Required Environment Variables
- `OPENAI_API_KEY` - Required for OpenAI API access
- Backend: Set in `python-backend/.env`
- Frontend: Uses backend proxy, no direct API key needed

### Optional Configuration
- `HOST` - Backend host (default: 0.0.0.0)
- `PORT` - Backend port (default: 8000)
- `RELOAD` - Enable auto-reload (default: true)

## Adding New Agents

1. **Add tools** (if needed) to appropriate category in `agent_service/tools/`
2. **Add instructions function** to `agent_service/instructions.py`
3. **Configure agent** in `agents_config.yaml`
4. **Update handoffs** in triage agent configuration if needed

## Key Files to Understand

### Backend Core
- `python-backend/agents_config.yaml` - Agent definitions and relationships
- `python-backend/agent_service/agent_factory.py` - Dynamic agent creation
- `python-backend/api.py` - FastAPI endpoints
- `python-backend/start.py` - Server startup script

### Frontend Core
- `ui/components/Chat.tsx` - Main chat interface
- `ui/components/agent-panel.tsx` - Agent visualization
- `ui/lib/api.ts` - Backend API client
- `ui/lib/types.ts` - TypeScript type definitions

### Tool System
- `python-backend/agent_service/tools/registry.py` - Tool discovery
- `python-backend/agent_service/tools/customer_service.py` - Core customer tools
- `python-backend/agent_service/tools/information.py` - Information retrieval tools

## Current Development Status and Roadmap

### Completed Features
- ✅ **Dynamic Agent Creation**: Agents can now be added through YAML configuration without modifying core code
- ✅ **Automatic Tool Discovery**: Tools are automatically registered when placed in the appropriate category modules

### Planned Backend Enhancements
- **Context Management Improvements**: Support customizable context according to the agent's needs
- **Specialized Guardrail Agent**: Implement a dedicated agent to handle security and relevance checking
- **Multi-Model Support**: Extend beyond OpenAI to support Anthropic Claude and other language models
- **Enhanced Tool Ecosystem**:
  - Web search capabilities for real-time information retrieval
  - File operation tools for document handling and processing
  - Presentation generation tools for creating slides and visual content
  - Image generation integration for visual responses

### Planned Frontend Improvements
- **Interactive Conversation Management**: Enable editing, re-running, and real-time streaming of agent responses
- **Rich Media Support**: 
  - File upload functionality for customers to share documents
  - Display capabilities for files, images, and generated content
- **Advanced Agent Interface**: Enhanced visualization and potential configuration of agent tools and behaviors
- **Session Management**: Implement chat history persistence and conversation room functionality

## Development Workflow

1. Backend changes require Poetry environment (`poetry shell`)
2. Frontend changes use npm/pnpm standard workflow
3. Agent modifications are primarily YAML configuration changes
4. New tools require Python implementation + registry update + YAML configuration
5. Run linting/formatting before commits: `poetry run black .` and `poetry run isort .` for Python