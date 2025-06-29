#!/usr/bin/env python3
"""
Startup script for the Customer Service Agents Demo backend.
This script loads environment variables and starts the FastAPI server.
"""

import os
import uvicorn
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"Starting server on {host}:{port}")
    print(f"Reload enabled: {reload}")
    
    # Ensure OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set!")
        print("Please set your OpenAI API key in a .env file or environment variable.")
    
    # Start the server
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main() 