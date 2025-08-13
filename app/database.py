"""
Database Configuration
======================

Database connection and session management for the e-commerce application.
This module sets up SQLModel/SQLAlchemy for database operations.

Author: bug6129
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")

# Create engine
# For SQLite, we need to enable foreign key constraints
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

def create_db_and_tables():
    """
    Create database tables.
    
    This function creates all tables defined in the models.
    Call this on application startup.
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    This function provides a database session for each request
    and ensures proper cleanup.
    
    Yields:
        Database session
    """
    with Session(engine) as session:
        yield session