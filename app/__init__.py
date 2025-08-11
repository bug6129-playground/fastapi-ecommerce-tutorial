"""
FastAPI E-Commerce Tutorial - Main Application Package
=====================================================

This package contains the main FastAPI application and all its components.

Package Structure:
- main.py: FastAPI application entry point and configuration
- database.py: Database connection and session management
- config.py: Application configuration and environment variables
- models/: Database models using SQLModel
- routers/: API route handlers organized by feature
- schemas/: Pydantic models for request/response validation
- services/: Business logic layer
- utils/: Utility functions and helpers

Author: bug6129
License: MIT
"""

# Package version
__version__ = "1.0.0"

# Package metadata
__author__ = "bug6129"
__description__ = "A comprehensive FastAPI e-commerce tutorial application"

# Export commonly used components for easier imports
# These will be available when someone does: from app import ...
from .config import settings

# Note: We don't import database or models here to avoid circular imports
# and to ensure proper initialization order

__all__ = [
    "settings",
    "__version__",
    "__author__",
    "__description__"
]