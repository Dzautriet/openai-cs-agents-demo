#!/bin/bash

# Customer Service Agents Demo - Quick Start Script
# This script will set up and run the application

set -e  # Exit on any error

echo "🚀 Customer Service Agents Demo - Quick Start"
echo "============================================="

# Check if .env files exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and set your OPENAI_API_KEY"
fi

if [ ! -f "python-backend/.env" ]; then
    echo "📝 Creating python-backend/.env file from template..."
    cp python-backend/.env.example python-backend/.env
    echo "⚠️  Please edit python-backend/.env and set your OPENAI_API_KEY"
fi

# Check if OpenAI API key is set
if ! grep -q "sk-" .env 2>/dev/null || ! grep -q "sk-" python-backend/.env 2>/dev/null; then
    echo ""
    echo "❌ OpenAI API key not found!"
    echo "Please set your OPENAI_API_KEY in both .env files:"
    echo "  - .env"
    echo "  - python-backend/.env"
    echo ""
    echo "Get your API key from: https://platform.openai.com/api-keys"
    exit 1
fi

# Check prerequisites
echo ""
echo "🔍 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Poetry
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is required but not installed."
    echo "Install it with: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "Install it from: https://nodejs.org/ or use brew install node"
    exit 1
fi

echo "✅ All prerequisites found!"

# Setup backend
echo ""
echo "🐍 Setting up Python backend..."
cd python-backend

if [ ! -f "poetry.lock" ]; then
    echo "📦 Installing Python dependencies with Poetry..."
    poetry install
else
    echo "📦 Python dependencies already installed"
fi

cd ..

# Setup frontend
echo ""
echo "🌐 Setting up frontend..."
cd ui

if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    if command -v pnpm &> /dev/null; then
        echo "Using pnpm..."
        pnpm install
    elif command -v bun &> /dev/null; then
        echo "Using bun..."
        bun install
    else
        echo "Using npm..."
        npm install
    fi
else
    echo "📦 Node.js dependencies already installed"
fi

cd ..

# Start the application
echo ""
echo "🎉 Setup complete! Starting the application..."
echo ""
echo "Frontend will be available at: http://localhost:3000"
echo "Backend will be available at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

cd ui
if command -v pnpm &> /dev/null; then
    pnpm dev
elif command -v bun &> /dev/null; then
    bun dev
else
    npm run dev
fi 