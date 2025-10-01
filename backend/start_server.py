#!/usr/bin/env python3
"""
GaaS Backend Startup Script
Handles initialization and startup of the FastAPI backend server.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✓ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def create_directories():
    """Create required directories if they don't exist."""
    directories = ['policies', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Directory '{directory}' ready")

def check_environment():
    """Check environment configuration."""
    env_file = Path('config/.env')
    if not env_file.exists():
        print("⚠ Warning: .env file not found")
        print("Using default configuration")
    else:
        print("✓ Environment configuration found")

def start_server(host="0.0.0.0", port=8000, reload=True):
    """Start the FastAPI server."""
    print(f"Starting GaaS Backend server on {host}:{port}")
    print(f"Reload mode: {'enabled' if reload else 'disabled'}")
    print("\nAPI Documentation will be available at:")
    print(f"  - Swagger UI: http://{host}:{port}/docs")
    print(f"  - ReDoc: http://{host}:{port}/redoc")
    print(f"  - Health Check: http://{host}:{port}/health")
    print("\nPress Ctrl+C to stop the server\n")

    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n✓ Server stopped gracefully")
    except Exception as e:
        print(f"✗ Server error: {e}")
        sys.exit(1)

def main():
    """Main startup function."""
    print("=" * 50)
    print("GaaS Backend - Governance-as-a-Service")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Create required directories
    create_directories()

    # Check environment
    check_environment()

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Start GaaS Backend Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=8000, help='Port number')
    parser.add_argument('--no-reload', action='store_true', help='Disable auto-reload')

    args = parser.parse_args()

    # Start server
    start_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload
    )

if __name__ == "__main__":
    main()
