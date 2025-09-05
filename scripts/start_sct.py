#!/usr/bin/env python3
"""
SyntheticCodingTeam Startup Helper
Simplifies starting the SCT service with proper configuration and monitoring.
"""

import os
import sys
import time
import subprocess
import argparse
import signal
from pathlib import Path
import requests
import json
from typing import Optional, Dict, Any

class SCTStarter:
    """Helper class to start and manage SCT service."""
    
    def __init__(self, port: int = 8000, env_file: str = ".env", docker: bool = False):
        self.port = port
        self.env_file = env_file
        self.docker = docker
        self.process = None
        self.service_url = f"http://localhost:{port}"
        
    def load_environment(self) -> Dict[str, str]:
        """Load environment variables from .env file."""
        env_vars = os.environ.copy()
        
        env_path = Path(self.env_file)
        if env_path.exists():
            print(f"📄 Loading environment from {self.env_file}")
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
            print("✅ Environment loaded")
        else:
            print(f"⚠️ No {self.env_file} file found")
            
        # Validate required variables
        required = ["GITHUB_TOKEN", "OPENAI_API_KEY", "GITHUB_WEBHOOK_SECRET"]
        missing = [var for var in required if not env_vars.get(var) and not env_vars.get(var.replace("_", "_PERSONAL_ACCESS_"))]
        
        if missing:
            print(f"❌ Missing required environment variables: {', '.join(missing)}")
            print("   Please set these in your .env file")
            return None
            
        return env_vars
    
    def check_port(self) -> bool:
        """Check if port is available."""
        try:
            # Try to connect to the port
            response = requests.get(f"{self.service_url}/health", timeout=1)
            if response.status_code == 200:
                print(f"⚠️ Service already running on port {self.port}")
                return False
        except:
            # Port is free
            return True
            
        # Kill existing process on port if needed
        print(f"🔧 Clearing port {self.port}...")
        subprocess.run(f"lsof -ti:{self.port} | xargs kill -9", 
                      shell=True, capture_output=True)
        time.sleep(1)
        return True
    
    def start_docker(self, env_vars: Dict[str, str]) -> bool:
        """Start SCT using Docker."""
        print("🐳 Starting SCT with Docker...")
        
        # Build Docker image
        print("   Building Docker image...")
        build_cmd = ["docker", "build", "-t", "sct:latest", "."]
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Docker build failed: {result.stderr}")
            return False
            
        print("✅ Docker image built")
        
        # Run Docker container
        print("   Starting container...")
        run_cmd = [
            "docker", "run",
            "--name", "sct-service",
            "--rm",
            "-d",
            "-p", f"{self.port}:8000",
        ]
        
        # Add environment variables
        for key, value in env_vars.items():
            if key.startswith("GITHUB") or key.startswith("OPENAI"):
                run_cmd.extend(["-e", f"{key}={value}"])
                
        run_cmd.append("sct:latest")
        
        result = subprocess.run(run_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Docker run failed: {result.stderr}")
            return False
            
        container_id = result.stdout.strip()
        print(f"✅ Container started: {container_id[:12]}")
        
        # Store container ID for cleanup
        self.container_id = container_id
        return True
    
    def start_local(self, env_vars: Dict[str, str]) -> bool:
        """Start SCT locally with uvicorn."""
        print("🚀 Starting SCT locally...")
        
        # Start uvicorn process
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app",
            "--host", "0.0.0.0",
            "--port", str(self.port),
            "--log-level", "info"
        ]
        
        print(f"   Command: {' '.join(cmd)}")
        
        self.process = subprocess.Popen(
            cmd,
            env=env_vars,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Monitor startup output
        print("   Monitoring startup...")
        return True
    
    def wait_for_service(self, timeout: int = 60) -> bool:
        """Wait for service to be ready."""
        print(f"⏳ Waiting for service at {self.service_url}")
        
        start_time = time.time()
        last_log_time = start_time
        
        while time.time() - start_time < timeout:
            # Check if service is ready
            try:
                response = requests.get(f"{self.service_url}/health", timeout=1)
                if response.status_code == 200:
                    print(f"✅ Service ready in {int(time.time() - start_time)}s")
                    
                    # Show service info
                    data = response.json()
                    print(f"\n📊 Service Status:")
                    print(f"   Status: {data.get('status', 'unknown')}")
                    print(f"   Version: {data.get('version', 'unknown')}")
                    
                    if 'dependencies' in data:
                        deps = data['dependencies']
                        print(f"   GitHub: {'✅' if deps.get('github', {}).get('status') == 'healthy' else '❌'}")
                        print(f"   OpenAI: {'✅' if deps.get('openai', {}).get('status') == 'healthy' else '❌'}")
                    
                    return True
            except requests.exceptions.RequestException:
                pass
            
            # Check if process died (local mode)
            if self.process and self.process.poll() is not None:
                print(f"❌ Service process died with code {self.process.returncode}")
                
                # Print last output
                if self.process.stdout:
                    output = self.process.stdout.read()
                    if output:
                        print("\nLast output:")
                        print(output[-500:])
                return False
            
            # Print progress
            if time.time() - last_log_time > 5:
                elapsed = int(time.time() - start_time)
                print(f"   Still waiting... ({elapsed}s)")
                last_log_time = time.time()
                
                # Read some output if available
                if self.process and self.process.stdout:
                    import select
                    if select.select([self.process.stdout], [], [], 0)[0]:
                        line = self.process.stdout.readline()
                        if line:
                            print(f"   > {line.strip()}")
            
            time.sleep(1)
        
        print(f"❌ Service failed to start within {timeout}s")
        return False
    
    def show_endpoints(self):
        """Display available API endpoints."""
        print(f"\n🌐 API Endpoints:")
        print(f"   Health:  {self.service_url}/health")
        print(f"   Docs:    {self.service_url}/docs")
        print(f"   Webhook: {self.service_url}/api/webhook/github")
        print(f"   Debug:   {self.service_url}/api/debug/status")
        print(f"\n📝 Logs:")
        print(f"   View logs: {self.service_url}/api/debug/logs")
        print(f"   Set level: {self.service_url}/api/debug/log-level")
    
    def monitor_service(self):
        """Monitor service output."""
        print(f"\n📊 Monitoring service (Ctrl+C to stop)...")
        print("=" * 60)
        
        try:
            if self.process:
                # Monitor local process
                for line in iter(self.process.stdout.readline, ''):
                    if line:
                        print(line.strip())
            elif self.docker and hasattr(self, 'container_id'):
                # Monitor Docker logs
                log_cmd = ["docker", "logs", "-f", self.container_id]
                subprocess.run(log_cmd)
        except KeyboardInterrupt:
            print("\n⏸️ Monitoring stopped")
    
    def cleanup(self):
        """Clean up resources."""
        print("\n🛑 Shutting down SCT...")
        
        if self.docker and hasattr(self, 'container_id'):
            # Stop Docker container
            subprocess.run(["docker", "stop", self.container_id], 
                         capture_output=True)
            print("✅ Docker container stopped")
        elif self.process:
            # Stop local process
            self.process.terminate()
            time.sleep(2)
            if self.process.poll() is None:
                self.process.kill()
            print("✅ Local process stopped")
    
    def start(self) -> bool:
        """Start the SCT service."""
        print("\n" + "=" * 60)
        print("🚀 SyntheticCodingTeam Startup Helper")
        print("=" * 60)
        
        # Load environment
        env_vars = self.load_environment()
        if not env_vars:
            return False
        
        # Check port availability
        if not self.check_port():
            return False
        
        # Start service
        if self.docker:
            if not self.start_docker(env_vars):
                return False
        else:
            if not self.start_local(env_vars):
                return False
        
        # Wait for service to be ready
        if not self.wait_for_service():
            self.cleanup()
            return False
        
        # Show available endpoints
        self.show_endpoints()
        
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Start SyntheticCodingTeam service")
    parser.add_argument("--port", type=int, default=8000, help="Port to run on (default: 8000)")
    parser.add_argument("--env", default=".env", help="Environment file (default: .env)")
    parser.add_argument("--docker", action="store_true", help="Run with Docker")
    parser.add_argument("--monitor", action="store_true", help="Monitor service output")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't cleanup on exit")
    
    args = parser.parse_args()
    
    # Create starter
    starter = SCTStarter(port=args.port, env_file=args.env, docker=args.docker)
    
    # Set up signal handlers
    def signal_handler(sig, frame):
        if not args.no_cleanup:
            starter.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start service
    if not starter.start():
        print("\n❌ Failed to start SCT service")
        sys.exit(1)
    
    print("\n✅ SCT service is running!")
    
    # Monitor if requested
    if args.monitor:
        starter.monitor_service()
    else:
        print("\nPress Ctrl+C to stop the service")
        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    
    # Cleanup
    if not args.no_cleanup:
        starter.cleanup()


if __name__ == "__main__":
    main()