"""Authentication module with password validation."""

import re


def validate_password(password):
    """Validate password format - CURRENT VERSION HAS BUG!"""
    if len(password) < 8:
        return False
    
    # BUG: Only allows alphanumeric - rejects special characters!
    return password.isalnum()  # This is the bug!


def authenticate_user(username, password):
    """Authenticate user with username and password."""
    if not validate_password(password):
        raise ValueError("Invalid password format")
    
    # Simulate authentication logic
    return {"username": username, "authenticated": True}


def hash_password(password):
    """Hash password for storage.""" 
    # Simplified for demo
    return f"hashed_{password}"
