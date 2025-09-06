#!/usr/bin/env python3
"""
SyntheticCodingTeam Startup Script

Proper startup script that loads environment variables and starts the SCT service.
"""

import os
import sys
import subprocess
from pathlib import Path


def load_env_file(env_file_path=".env"):
    """Load environment variables from .env file using python-dotenv if available."""
    # First try using python-dotenv (more robust)
    try:
        from dotenv import load_dotenv
        if load_dotenv(env_file_path):
            print(f"✅ Environment variables loaded from {env_file_path} (using python-dotenv)")
            return True
    except ImportError:
        pass
    
    # Fallback to manual loading
    env_file = Path(env_file_path)
    if env_file.exists():
        print(f"Loading environment variables from {env_file_path} (manual method)...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Handle quoted values
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key] = value
        print("✅ Environment variables loaded successfully")
        return True
    else:
        print(f"⚠️  Warning: {env_file_path} not found")
        return False


def check_required_env_vars():
    """Check that required environment variables are set."""
    required_vars = [
        ('OPENAI_API_KEY', 'OpenAI API key'),
        ('GITHUB_PERSONAL_ACCESS_TOKEN', 'GitHub personal access token'),
        ('GITHUB_WEBHOOK_SECRET', 'GitHub webhook secret')
    ]
    
    missing_vars = []
    for var, description in required_vars:
        if not os.getenv(var):
            missing_vars.append((var, description))
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var, desc in missing_vars:
            print(f"   - {var} ({desc})")
        return False
    
    print("✅ All required environment variables are set")
    return True


def start_sct_service(host="0.0.0.0", port=8000, reload=False):
    """Start the SCT service using uvicorn."""
    print("🚀 Starting SyntheticCodingTeam service...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Auto-reload: {reload}")
    
    if reload:
        print("⚠️  Warning: Auto-reload can cause issues with environment variables")
        print("   Consider using --no-reload for production")
    
    print("=" * 50)
    
    # Build uvicorn command
    cmd = [
        "python", "-m", "uvicorn", "main:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    # Pass current environment to subprocess (including loaded .env vars)
    env = os.environ.copy()
    
    # Start the service
    try:
        subprocess.run(cmd, check=True, env=env)
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Service failed to start: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    print("=" * 60)
    print("🤖 SYNTHETICCODINGTEAM STARTUP")
    print("=" * 60)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Start SyntheticCodingTeam service')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--env-file', default='.env', help='Path to .env file')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_env_file(args.env_file)
    
    # Check required environment variables
    if not check_required_env_vars():
        print("❌ Cannot start service without required environment variables")
        sys.exit(1)
    
    # Start the service
    start_sct_service(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()