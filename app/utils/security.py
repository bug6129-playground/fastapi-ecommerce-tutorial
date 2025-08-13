"""
Security Utilities
==================

Password hashing, validation, and security-related helper functions.
This module provides secure password handling using industry-standard practices.

Author: bug6129
"""

from passlib.context import CryptContext
from typing import Optional
import secrets
import string

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hashed password
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)

def generate_verification_token(length: int = 32) -> str:
    """
    Generate a secure random token for email verification.
    
    Args:
        length: Length of the token to generate
        
    Returns:
        Random alphanumeric token
        
    Example:
        >>> token = generate_verification_token()
        >>> len(token)
        32
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def validate_password_strength(password: str) -> dict:
    """
    Validate password strength and return detailed feedback.
    
    Args:
        password: Password to validate
        
    Returns:
        Dictionary with validation results and feedback
        
    Example:
        >>> result = validate_password_strength("WeakPass")
        >>> result['is_valid']
        False
        >>> result = validate_password_strength("StrongPass123!")
        >>> result['is_valid']
        True
    """
    issues = []
    score = 0
    
    # Check length
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    else:
        score += 1
    
    # Check for uppercase letter
    if not any(c.isupper() for c in password):
        issues.append("Password must contain at least one uppercase letter")
    else:
        score += 1
    
    # Check for lowercase letter
    if not any(c.islower() for c in password):
        issues.append("Password must contain at least one lowercase letter")
    else:
        score += 1
    
    # Check for digit
    if not any(c.isdigit() for c in password):
        issues.append("Password must contain at least one digit")
    else:
        score += 1
    
    # Check for special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        issues.append("Password should contain at least one special character")
    else:
        score += 1
    
    # Calculate strength
    strength_levels = {0: "Very Weak", 1: "Weak", 2: "Fair", 3: "Good", 4: "Strong", 5: "Very Strong"}
    strength = strength_levels.get(score, "Unknown")
    
    return {
        "is_valid": len(issues) == 0,
        "score": score,
        "max_score": 5,
        "strength": strength,
        "issues": issues,
        "feedback": "Password meets all requirements" if len(issues) == 0 else f"{len(issues)} issue(s) found"
    }

def sanitize_email(email: str) -> str:
    """
    Sanitize and normalize email address.
    
    Args:
        email: Email address to sanitize
        
    Returns:
        Cleaned and normalized email address
        
    Example:
        >>> sanitize_email("  User@EXAMPLE.COM  ")
        'user@example.com'
    """
    return email.strip().lower()

def is_safe_username(username: str) -> bool:
    """
    Check if username is safe (no harmful characters).
    
    Args:
        username: Username to validate
        
    Returns:
        True if username is safe, False otherwise
        
    Example:
        >>> is_safe_username("john_doe123")
        True
        >>> is_safe_username("john<script>")
        False
    """
    # Allow alphanumeric, underscore, hyphen, and periods
    allowed_chars = set(string.ascii_letters + string.digits + '_-.')
    return all(c in allowed_chars for c in username)

class SecurityConfig:
    """Security configuration constants."""
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 100
    
    # Token settings
    EMAIL_VERIFICATION_TOKEN_LENGTH = 32
    PASSWORD_RESET_TOKEN_LENGTH = 32
    
    # Rate limiting (requests per minute)
    LOGIN_ATTEMPTS_LIMIT = 5
    REGISTRATION_ATTEMPTS_LIMIT = 3
    PASSWORD_RESET_ATTEMPTS_LIMIT = 3
    
    # Session settings
    SESSION_TIMEOUT_MINUTES = 60
    REMEMBER_ME_DAYS = 30