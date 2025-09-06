"""
Environment variable loader that runs at import time.

This module automatically loads .env variables when imported,
ensuring they're available to all subsequent imports including
uvicorn child processes.
"""

import os
from pathlib import Path


def load_env_variables():
    """Load environment variables from .env file if it exists."""
    env_file = Path(".env")
    
    if not env_file.exists():
        return False
    
    try:
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
                    # Only set if not already set (don't override existing env vars)
                    if key not in os.environ:
                        os.environ[key] = value
        return True
    except Exception:
        return False


# Load environment variables immediately when this module is imported
_loaded = load_env_variables()