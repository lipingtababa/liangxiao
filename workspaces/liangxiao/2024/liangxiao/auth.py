"""Authentication module for user login system."""

import hashlib
import re
from typing import Dict, Optional


def validate_password(password: str) -> bool:
    """
    Validate password format.
    
    CURRENT BUG: Only accepts alphanumeric characters!
    This rejects secure passwords with special characters.
    """
    if len(password) < 8:
        return False
    
    # BUG: This line rejects all special characters!
    # This is exactly what causes the reported issue
    return password.isalnum()


def hash_password(password: str) -> str:
    """Hash password for secure storage."""
    salt = "static_salt_for_demo"  # In real app, use random salt
    return hashlib.sha256((password + salt).encode()).hexdigest()


def authenticate_user(username: str, password: str) -> Dict[str, any]:
    """
    Authenticate user with username and password.
    
    Raises ValueError if password format is invalid.
    """
    if not validate_password(password):
        raise ValueError("Invalid password format")
    
    # Simulate database lookup
    hashed = hash_password(password)
    
    return {
        "username": username,
        "authenticated": True,
        "password_hash": hashed,
        "login_time": "2024-01-01T12:00:00Z"
    }


def change_password(username: str, old_password: str, new_password: str) -> bool:
    """Change user password with validation."""
    # Authenticate with old password first
    try:
        authenticate_user(username, old_password)
    except ValueError:
        return False
    
    # Validate new password
    if not validate_password(new_password):
        raise ValueError("New password format is invalid")
    
    # In real app: update database
    return True
