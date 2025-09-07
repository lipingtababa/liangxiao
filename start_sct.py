#!/usr/bin/env python3
"""
SyntheticCodingTeam Startup Script

Proper startup script that loads environment variables and starts the SCT service.
"""

import os
import sys
import subprocess
import signal
import psutil
from pathlib import Path

# Setup logging early
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.unified_logging import setup_unified_logging


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


def kill_existing_sct_processes():
    """Kill any existing SCT processes to avoid conflicts."""
    killed_count = 0
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline'] or []
                cmdline_str = ' '.join(cmdline).lower()
                
                # Check if this is an SCT process
                if any(indicator in cmdline_str for indicator in [
                    'uvicorn main:app',
                    'start_sct.py',
                    'python main.py'
                ]) and proc.pid != os.getpid():
                    
                    print(f"🔄 Killing existing SCT process: PID {proc.pid}")
                    proc.terminate()
                    
                    # Wait for graceful termination
                    try:
                        proc.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        print(f"⚡ Force killing process: PID {proc.pid}")
                        proc.kill()
                    
                    killed_count += 1
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
    except Exception as e:
        print(f"⚠️  Warning: Could not check for existing processes: {e}")
    
    if killed_count > 0:
        print(f"✅ Killed {killed_count} existing SCT process(es)")
    else:
        print("ℹ️  No existing SCT processes found")


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
        "--port", str(port),
        "--log-level", "debug"
    ]
    
    if reload:
        cmd.append("--reload")
    
    # Pass current environment to subprocess (including loaded .env vars)
    env = os.environ.copy()
    
    # Start the service
    try:
        subprocess.run(cmd, check=True, env=env, stdout=sys.stdout, stderr=sys.stderr)
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Service failed to start: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    # Setup logging first
    setup_unified_logging(level="INFO")
    
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
    
    # Kill any existing SCT processes
    kill_existing_sct_processes()
    
    # Start the service
    start_sct_service(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()