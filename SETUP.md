# Customer Service Agents Demo - Setup Guide

This guide will help you set up the Customer Service Agents Demo using modern development tools including Poetry for Python dependency management and proper environment variable configuration.

## Prerequisites

Before you begin, make sure you have the following installed:

1. **Python 3.9+** - Check with `python --version`
2. **Poetry** - Python dependency management tool
3. **Node.js 18+** - For the frontend (includes npm)
4. **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)

### Installing Prerequisites

#### Install Poetry (Python dependency manager)
```bash
# Using the official installer (recommended)
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip
pip install poetry

# Or using uv (if you have it)
uv tool install poetry
```

#### Install Node.js and npm
```bash
# Using Homebrew (macOS)
brew install node

# Or download from https://nodejs.org/
# Or use a version manager like nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts
nvm use --lts
```

#### Alternative: Using pnpm or bun instead of npm
```bash
# Install pnpm (faster alternative to npm)
npm install -g pnpm

# Or install bun (even faster)
curl -fsSL https://bun.sh/install | bash
```

## Setup Instructions

### 1. Clone and Navigate to the Repository
```bash
git clone <your-fork-url>
cd openai-cs-agents-demo
```

### 2. Set Up Environment Variables

Copy the example environment files and configure them:

```bash
# Root environment file
cp .env.example .env

# Backend environment file
cp python-backend/.env.example python-backend/.env
```

Edit both `.env` files and set your OpenAI API key:
```bash
# In both .env files, replace:
OPENAI_API_KEY=your_openai_api_key_here
# With your actual API key:
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Set Up the Python Backend

```bash
cd python-backend

# Install dependencies using Poetry
poetry install

# Activate the virtual environment
poetry shell

# Verify installation
poetry show
```

### 4. Set Up the Frontend

```bash
cd ../ui

# Using npm
npm install

# Or using pnpm (faster)
pnpm install

# Or using bun (fastest)
bun install
```

## Running the Application

### Option 1: Run Both Services Together (Recommended)

From the `ui` directory:
```bash
# Using npm
npm run dev

# Using pnpm
pnpm dev

# Using bun
bun dev
```

This will start both the frontend (http://localhost:3000) and backend (http://localhost:8000) simultaneously.

### Option 2: Run Services Separately

#### Start the Backend
```bash
cd python-backend

# Using Poetry
poetry run python start.py

# Or using the traditional uvicorn command
poetry run uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

#### Start the Frontend
```bash
cd ui

# Using npm
npm run dev:next

# Using pnpm
pnpm dev:next

# Using bun
bun dev:next
```

## Development Tools

### Python Backend Tools

The Poetry configuration includes development tools for code quality:

```bash
cd python-backend

# Format code with Black
poetry run black .

# Sort imports with isort
poetry run isort .

# Type checking with mypy
poetry run mypy .

# Run tests
poetry run pytest
```

### Frontend Tools

```bash
cd ui

# Lint the code
npm run lint

# Build for production
npm run build

# Start production server
npm run start
```

## Environment Variables Reference

### Root `.env` file
- `OPENAI_API_KEY`: Your OpenAI API key
- `BACKEND_HOST`: Backend host (default: 0.0.0.0)
- `BACKEND_PORT`: Backend port (default: 8000)
- `FRONTEND_PORT`: Frontend port (default: 3000)
- `ALLOWED_ORIGINS`: CORS allowed origins (default: http://localhost:3000)
- `NODE_ENV`: Node environment (development/production)
- `PYTHON_ENV`: Python environment (development/production)

### Backend `.env` file
- `OPENAI_API_KEY`: Your OpenAI API key
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable auto-reload (default: true)
- `ALLOWED_ORIGINS`: CORS allowed origins
- `PYTHON_ENV`: Environment (development/production)

## Troubleshooting

### Common Issues

1. **Poetry not found**: Make sure Poetry is installed and in your PATH
2. **OpenAI API key not working**: Verify your API key is correct and has sufficient credits
3. **Port already in use**: Change the port numbers in your `.env` files
4. **CORS errors**: Check that `ALLOWED_ORIGINS` includes your frontend URL

### Useful Commands

```bash
# Check Poetry configuration
poetry config --list

# Update dependencies
poetry update

# Add a new dependency
poetry add package-name

# Remove a dependency
poetry remove package-name

# Show dependency tree
poetry show --tree

# Check for outdated packages (npm)
npm outdated

# Update packages (npm)
npm update
```

## Next Steps

Once everything is running:

1. Open http://localhost:3000 in your browser
2. Try the demo flows described in the main README.md
3. Explore the agent configurations in `python-backend/main.py`
4. Customize the agents, tools, and guardrails for your use case

## Production Deployment

For production deployment, consider:

1. Set `NODE_ENV=production` and `PYTHON_ENV=production`
2. Use a production WSGI server like Gunicorn
3. Set up proper logging and monitoring
4. Use a production database instead of in-memory storage
5. Configure proper CORS origins for your domain
6. Use environment-specific `.env` files 