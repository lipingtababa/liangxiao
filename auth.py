"""Authentication module - Smart conservative fix for @ symbols."""

def validate_password(password):
    """Validate password format - FIXED to allow @ symbols."""
    if len(password) < 8:
        return False
    
    # SMART FIX: Conservative approach - allow @ symbol for email-style passwords
    # Minimal change that fixes the specific user issue
    return all(c.isalnum() or c == '@' for c in password)


def login_user(username, password):
    """Login user if password is valid.""" 
    if not validate_password(password):
        raise ValueError("Invalid password format")
    return {"user": username, "success": True}


if __name__ == "__main__":
    # Demo the fix working
    try:
        result = login_user("test@email.com", "mypass@123")
        print("Login successful:", result)  # Now works!
    except ValueError as e:
        print("Login failed:", e)
