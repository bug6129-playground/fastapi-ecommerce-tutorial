"""
User Database Models
===================

SQLModel models that define how user data is stored in the database.
These models represent the actual database tables and relationships.

Author: bug6129
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

class UserRole(str, Enum):
    """User role enumeration."""
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"

class UserStatus(str, Enum):
    """User account status."""
    PENDING = "pending"        # Email not verified
    ACTIVE = "active"          # Normal active user
    SUSPENDED = "suspended"    # Temporarily suspended
    BANNED = "banned"         # Permanently banned

# Base class for shared user fields
class UserBase(SQLModel):
    """Base user model with shared fields."""
    
    # Personal Information
    email: str = Field(unique=True, index=True, max_length=255)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    
    # Account Information
    role: UserRole = Field(default=UserRole.CUSTOMER)
    status: UserStatus = Field(default=UserStatus.PENDING)
    is_email_verified: bool = Field(default=False)
    
    # Profile Information
    phone: Optional[str] = Field(default=None, max_length=20)
    date_of_birth: Optional[datetime] = Field(default=None)
    
    # Preferences
    newsletter_subscribed: bool = Field(default=True)
    marketing_emails: bool = Field(default=False)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)

# Database table model
class User(UserBase, table=True):
    """User database table model."""
    
    __tablename__ = "users"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Authentication
    hashed_password: str = Field(max_length=255)
    
    # Relationships (we'll add these in future chapters)
    # addresses: List["Address"] = Relationship(back_populates="user")
    # orders: List["Order"] = Relationship(back_populates="customer")

# For creating users (excludes computed fields)
class UserCreate(UserBase):
    """Model for creating new users."""
    password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)
    terms_accepted: bool = Field(description="User must accept terms and conditions")

# For updating users (all fields optional)
class UserUpdate(SQLModel):
    """Model for updating existing users."""
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    date_of_birth: Optional[datetime] = Field(default=None)
    newsletter_subscribed: Optional[bool] = Field(default=None)
    marketing_emails: Optional[bool] = Field(default=None)

# Address model (for shipping addresses)
class AddressBase(SQLModel):
    """Base address model."""
    street_address: str = Field(max_length=200)
    apartment: Optional[str] = Field(default=None, max_length=50)
    city: str = Field(max_length=100)
    state_province: str = Field(max_length=100)
    postal_code: str = Field(max_length=20)
    country: str = Field(default="USA", max_length=100)
    is_default: bool = Field(default=False)

class Address(AddressBase, table=True):
    """Address database table."""
    
    __tablename__ = "addresses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    # user: User = Relationship(back_populates="addresses")